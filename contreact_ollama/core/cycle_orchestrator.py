# Standard library imports
from typing import List, Dict, Any, Tuple, Optional

# Local application imports
from contreact_ollama.constants import SYSTEM_PROMPT
from contreact_ollama.core.config import ExperimentConfig
from contreact_ollama.llm.ollama_interface import OllamaInterface
from contreact_ollama.llm.prompt_assembler import build_prompt
from contreact_ollama.llm.response_parser import parse_ollama_response
from contreact_ollama.logging.jsonl_logger import JsonlLogger, EventType
from contreact_ollama.state.agent_state import AgentState
from contreact_ollama.tools.tool_dispatcher import ToolDispatcher


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
        logger: Optional[JsonlLogger] = None
    ) -> None:
        """Initialize orchestrator with configuration and services.
        
        Args:
            config: Experiment configuration with run parameters
            ollama_interface: Interface for Ollama LLM interactions
            tool_dispatcher: Tool dispatcher for executing agent tools
            logger: Event logger (optional for now, required in production)
        """
        self.config = config
        self.ollama_interface = ollama_interface
        self.tool_dispatcher = tool_dispatcher
        self.logger = logger
    
    def run_experiment(self) -> None:
        """Main public method executing full experimental run from Cycle 1 to cycle_count.
        
        Iterates through cycles, executing each one and tracking completion.
        Logs CYCLE_START and CYCLE_END events for each cycle.
        """
        print(f"\nStarting experiment: {self.config.run_id}")
        print(f"Model: {self.config.model_name}")
        print(f"Total cycles: {self.config.cycle_count}\n")
        
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
            
            # Load state for this cycle
            agent_state = self._load_state(cycle_num)
            
            # Execute cycle (empty for now)
            agent_state = self._execute_cycle(agent_state)
            
            print(f"Cycle {cycle_num} finished.")
            
            # Log cycle end
            if self.logger:
                self.logger.log_event(
                    run_id=self.config.run_id,
                    cycle_number=cycle_num,
                    event_type=EventType.CYCLE_END,
                    payload={}
                )
        
        print(f"\n✓ Experiment {self.config.run_id} completed successfully")
        print(f"✓ Executed {self.config.cycle_count} cycles")
        if self.logger:
            print(f"✓ Log file: logs/{self.config.run_id}.jsonl")
    
    def _execute_cycle(self, agent_state: AgentState) -> AgentState:
        """Execute a single cycle of the ContReAct state machine.
        
        Implements the ReAct loop:
        1. Assemble prompt
        2. Invoke LLM
        3. Parse response
        4. If tool call: dispatch → append result → repeat from step 1
        5. If final reflection: exit loop
        
        Args:
            agent_state: Current agent state
            
        Returns:
            Updated agent state with final reflection
        """
        # ReAct loop - continues until agent provides final reflection
        while True:
            # ASSEMBLE_PROMPT
            messages = self._assemble_prompt(agent_state)
            
            # INVOKE_LLM
            response = self._invoke_llm(messages)
            
            # Log LLM invocation
            if self.logger:
                self.logger.log_event(
                    run_id=self.config.run_id,
                    cycle_number=agent_state.cycle_number,
                    event_type=EventType.LLM_INVOCATION,
                    payload={
                        "prompt_messages": messages,
                        "response_message": response.get("message", {}),
                        "model_options": self.config.model_options
                    }
                )
            
            # Append assistant's response to message history
            agent_state.message_history.append(response["message"])
            
            # PARSE_RESPONSE
            response_type, data = self._parse_response(response)
            
            if response_type == "TOOL_CALL":
                # Process each tool call
                for tool_call in data:
                    # DISPATCH_TOOL
                    tool_result = self._dispatch_tool(tool_call)
                    
                    # Log tool call
                    if self.logger:
                        self.logger.log_event(
                            run_id=self.config.run_id,
                            cycle_number=agent_state.cycle_number,
                            event_type=EventType.TOOL_CALL,
                            payload={
                                "tool_name": tool_call["function"]["name"],
                                "parameters": tool_call["function"]["arguments"],
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
    
    def _dispatch_tool(self, tool_call: Dict) -> str:
        """DISPATCH_TOOL: Invoke tool and return result.
        
        Args:
            tool_call: Tool call dict from Ollama response
                       Expected: {"function": {"name": "...", "arguments": {...}}}
            
        Returns:
            String result from tool execution
        """
        tool_name = tool_call["function"]["name"]
        arguments = tool_call["function"]["arguments"]
        
        result = self.tool_dispatcher.dispatch(tool_name, arguments)
        
        return result
    
    def _load_state(self, cycle_number: int) -> AgentState:
        """LOAD_STATE: Load or initialize AgentState.
        
        Args:
            cycle_number: Current cycle number (1-based)
            
        Returns:
            AgentState: Initialized state for this cycle
        """
        return AgentState(
            run_id=self.config.run_id,
            cycle_number=cycle_number,
            model_name=self.config.model_name,
            message_history=[],  # Empty for now, will be populated in later stories
            reflection_history=[]  # Empty for now, will be populated in later stories
        )
