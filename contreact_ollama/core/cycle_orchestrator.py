# Standard library imports
from typing import List, Dict, Any, Tuple, Optional

# Third-party imports
import numpy as np

# Local application imports
from contreact_ollama.constants import SYSTEM_PROMPT
from contreact_ollama.core.config import ExperimentConfig
from contreact_ollama.llm.ollama_interface import OllamaInterface
from contreact_ollama.llm.prompt_assembler import build_prompt
from contreact_ollama.llm.response_parser import parse_ollama_response
from contreact_ollama.logging.jsonl_logger import JsonlLogger, EventType
from contreact_ollama.state.agent_state import AgentState
from contreact_ollama.tools.tool_dispatcher import ToolDispatcher
from contreact_ollama.analysis.similarity_monitor import SimilarityMonitor


class CycleOrchestrator:
    """Manages execution of agent's operational cycles.
    
    The CycleOrchestrator is responsible for executing the full experimental run,
    coordinating the ContReAct state machine across multiple cycles.
    
    Attributes:
        config: Experiment configuration containing run parameters
        ollama_interface: Interface for LLM interactions
    """
    
    def __init__(
        self,
        config: ExperimentConfig,
        ollama_interface: OllamaInterface,
        tool_dispatcher: ToolDispatcher,
        logger: Optional[JsonlLogger] = None,
        similarity_monitor: Optional[SimilarityMonitor] = None
    ) -> None:
        """Initialize orchestrator with configuration and services.
        
        Args:
            config: Experiment configuration with run parameters
            ollama_interface: Interface for Ollama LLM interactions
            tool_dispatcher: Tool dispatcher for executing agent tools
            logger: Event logger (optional for now, required in production)
            similarity_monitor: Similarity monitor for diversity feedback (optional)
        """
        self.config = config
        self.ollama_interface = ollama_interface
        self.tool_dispatcher = tool_dispatcher
        self.logger = logger
        self.similarity_monitor = similarity_monitor
        
        # Storage for reflection embeddings
        self.reflection_embeddings: List[np.ndarray] = []
    
    def run_experiment(self) -> None:
        """Main public method executing full experimental run from Cycle 1 to cycle_count.
        
        Iterates through cycles, executing each one and tracking completion.
        Logs CYCLE_START and CYCLE_END events for each cycle.
        Maintains reflection_history continuity across cycles while resetting message_history.
        Includes diversity monitoring via similarity checking.
        """
        print(f"\nStarting experiment: {self.config.run_id}")
        print(f"Model: {self.config.model_name}")
        print(f"Total cycles: {self.config.cycle_count}\n")
        
        # Initialize reflection history to persist across cycles
        reflection_history = []
        diversity_feedback = None  # Feedback for next cycle
        
        for cycle_num in range(1, self.config.cycle_count + 1):
            # Log cycle start
            if self.logger:
                self.logger.log_event(
                    run_id=self.config.run_id,
                    cycle_number=cycle_num,
                    event_type=EventType.CYCLE_START,
                    payload={}
                )
            
            print(f"Cycle {cycle_num} starting...")
            
            # Load state for this cycle - always fresh message_history
            agent_state = self._load_state(cycle_num)
            # Restore reflection history from previous cycles
            agent_state.reflection_history = reflection_history.copy()
            
            # Execute cycle (diversity_feedback will be used in _assemble_prompt)
            agent_state = self._execute_cycle(agent_state, diversity_feedback)
            
            print(f"Cycle {cycle_num} finished.")
            
            # Extract final reflection for logging and persist it
            final_reflection = agent_state.reflection_history[-1] if agent_state.reflection_history else ""
            reflection_history = agent_state.reflection_history.copy()
            
            # Generate embedding and check similarity for NEXT cycle
            diversity_feedback = None
            if self.similarity_monitor and final_reflection:
                embedding = self.similarity_monitor.embedding_service.get_embedding(final_reflection)
                
                # Check similarity against historical embeddings
                diversity_feedback = self.similarity_monitor.check_similarity(
                    new_reflection_embedding=embedding,
                    historical_embeddings=self.reflection_embeddings
                )
                
                # Store this embedding for future comparisons
                self.reflection_embeddings.append(embedding)
                
                # Optional: log if feedback generated
                if diversity_feedback:
                    print(f"  [Diversity advisory triggered: similarity detected]")
            
            # Log cycle end with reflection and metrics
            if self.logger:
                payload = {
                    "final_reflection": final_reflection
                }
                
                # Include metrics if available
                if hasattr(agent_state, 'cycle_metrics'):
                    payload["metrics"] = agent_state.cycle_metrics
                
                self.logger.log_event(
                    run_id=self.config.run_id,
                    cycle_number=cycle_num,
                    event_type=EventType.CYCLE_END,
                    payload=payload
                )
        
        print(f"\n✓ Experiment {self.config.run_id} completed successfully")
        print(f"✓ Executed {self.config.cycle_count} cycles")
        if self.logger:
            print(f"✓ Log file: logs/{self.config.run_id}.jsonl")
    
    def _execute_cycle(self, agent_state: AgentState, diversity_feedback: Optional[str] = None) -> AgentState:
        """Execute a single cycle of the ContReAct state machine.
        
        Implements the ReAct loop:
        1. Assemble prompt
        2. Invoke LLM
        3. Parse response
        4. If tool call: dispatch → append result → repeat from step 1
        5. If final reflection: exit loop
        
        Args:
            agent_state: Current agent state
            diversity_feedback: Optional diversity feedback to include in prompt
            
        Returns:
            Updated agent state with final reflection
        """
        # Initialize metrics tracking for this cycle
        cycle_metrics = {
            "memory_ops_total": 0,
            "messages_to_operator": 0,
            "response_chars": 0,
            "memory_write_chars": 0
        }
        
        # ReAct loop - continues until agent provides final reflection
        while True:
            # ASSEMBLE_PROMPT
            messages = self._assemble_prompt(agent_state, diversity_feedback)
            
            # INVOKE_LLM
            response = self._invoke_llm(messages)
            
            # Log LLM invocation
            if self.logger:
                # Extract only JSON-serializable data from response
                message = response.get("message", {})
                serializable_message = {
                    "role": message.get("role", ""),
                    "content": message.get("content", "")
                }
                # Include tool_calls if present
                if "tool_calls" in message:
                    serializable_message["tool_calls"] = message["tool_calls"]
                
                self.logger.log_event(
                    run_id=self.config.run_id,
                    cycle_number=agent_state.cycle_number,
                    event_type=EventType.LLM_INVOCATION,
                    payload={
                        "prompt_messages": messages,
                        "response_message": serializable_message,
                        "model_options": self.config.model_options
                    }
                )
            
            # Append assistant's response to message history
            agent_state.message_history.append(response["message"])
            
            # Track response characters
            response_content = response["message"].get("content", "")
            cycle_metrics["response_chars"] += len(response_content)
            
            # PARSE_RESPONSE
            response_type, data = self._parse_response(response)
            
            if response_type == "TOOL_CALL":
                # Process each tool call
                for tool_call in data:
                    # Track metrics based on tool type
                    tool_name = tool_call["function"]["name"]
                    tool_args = tool_call["function"]["arguments"]
                    
                    # Count memory operations
                    if tool_name in ["write", "read", "list", "delete", "pattern_search"]:
                        cycle_metrics["memory_ops_total"] += 1
                        
                        # Track memory write characters
                        if tool_name == "write" and "value" in tool_args:
                            cycle_metrics["memory_write_chars"] += len(str(tool_args["value"]))
                    
                    # Count operator messages
                    if tool_name == "send_message_to_operator":
                        cycle_metrics["messages_to_operator"] += 1
                    
                    # DISPATCH_TOOL
                    tool_result = self._dispatch_tool(tool_call, agent_state)
                    
                    # Log tool call
                    if self.logger:
                        self.logger.log_event(
                            run_id=self.config.run_id,
                            cycle_number=agent_state.cycle_number,
                            event_type=EventType.TOOL_CALL,
                            payload={
                                "tool_name": tool_name,
                                "parameters": tool_args,
                                "output": tool_result
                            }
                        )
                    
                    # Append tool result to message history
                    agent_state.message_history.append({
                        "role": "tool",
                        "content": tool_result,
                        "tool_call_id": tool_call.get("id")
                    })
                
                # Continue loop - will call LLM again with tool results
                continue
                
            elif response_type == "FINAL_REFLECTION":
                # Agent has provided final reflection - exit loop
                # Store reflection (will be used in Story 1.9)
                agent_state.reflection_history.append(data)
                break
        
        # Store metrics in agent state for logging
        agent_state.cycle_metrics = cycle_metrics
        
        return agent_state
    
    def _assemble_prompt(self, agent_state: AgentState, diversity_feedback: Optional[str] = None) -> List[Dict]:
        """ASSEMBLE_PROMPT: Construct full context for LLM.
        
        Args:
            agent_state: Current agent state
            diversity_feedback: Optional feedback from similarity monitor
            
        Returns:
            List of message dicts for ollama.chat
        """
        # Get tool definitions
        tool_definitions = self.tool_dispatcher.get_tool_definitions()
        
        # Build prompt
        messages = build_prompt(
            agent_state=agent_state,
            system_prompt=SYSTEM_PROMPT,
            tool_definitions=tool_definitions,
            diversity_feedback=diversity_feedback
        )
        
        return messages
    
    def _invoke_llm(self, messages: List[Dict]) -> Dict:
        """INVOKE_LLM: Send prompt to Ollama server.
        
        Args:
            messages: Formatted message list
            
        Returns:
            Response dict from Ollama
        """
        response = self.ollama_interface.execute_chat_completion(
            model_name=self.config.model_name,
            messages=messages,
            tools=self.tool_dispatcher.get_tool_definitions(),
            options=self.config.model_options
        )
        
        return response
    
    def _parse_response(self, response: Dict) -> Tuple[str, Any]:
        """PARSE_RESPONSE: Determine if response contains tool calls or final reflection.
        
        Args:
            response: Response from Ollama
            
        Returns:
            Tuple of (response_type, data)
        """
        return parse_ollama_response(response)
    
    def _dispatch_tool(self, tool_call: Dict, agent_state: AgentState) -> str:
        """DISPATCH_TOOL: Invoke tool and return result.
        
        Args:
            tool_call: Tool call dict from Ollama response
                       Expected: {"function": {"name": "...", "arguments": {...}}}
            agent_state: Current agent state for context (run_id, cycle_number)
            
        Returns:
            String result from tool execution
        """
        tool_name = tool_call["function"]["name"]
        arguments = tool_call["function"]["arguments"]
        
        result = self.tool_dispatcher.dispatch(
            tool_name,
            arguments,
            run_id=agent_state.run_id,
            cycle_number=agent_state.cycle_number
        )
        
        return result
    
    def _load_state(self, cycle_number: int) -> AgentState:
        """LOAD_STATE: Load or initialize AgentState.
        
        Args:
            cycle_number: Current cycle number (1-based)
            
        Returns:
            AgentState: Initialized state for this cycle with fresh message_history
        """
        return AgentState(
            run_id=self.config.run_id,
            cycle_number=cycle_number,
            model_name=self.config.model_name,
            message_history=[],  # Always starts empty - populated during cycle execution
            reflection_history=[]  # Initialized empty - run_experiment() restores from previous cycles
        )
