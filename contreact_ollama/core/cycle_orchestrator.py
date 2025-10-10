# Standard library imports
from typing import Optional

# Local application imports
from contreact_ollama.core.config import ExperimentConfig
from contreact_ollama.llm.ollama_interface import OllamaInterface
from contreact_ollama.logging.jsonl_logger import JsonlLogger, EventType
from contreact_ollama.state.agent_state import AgentState


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
        logger: Optional[JsonlLogger] = None
    ) -> None:
        """Initialize orchestrator with configuration and services.
        
        Args:
            config: Experiment configuration with run parameters
            ollama_interface: Interface for Ollama LLM interactions
            logger: Event logger (optional for now, required in production)
        """
        self.config = config
        self.ollama_interface = ollama_interface
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
        
        Args:
            agent_state: Current agent state
            
        Returns:
            AgentState: Updated agent state after cycle execution
            
        Note:
            This is a basic implementation for Story 1.4.
            Full state machine logic will be added in later stories.
        """
        # For now, just return the state unchanged
        # Later stories will add: prompt assembly, LLM invocation, tool dispatch, etc.
        return agent_state
    
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
