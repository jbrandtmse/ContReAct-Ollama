# Parameter Tuning Guide for Autonomous Agents

This guide provides recommendations for tuning LLM parameters when running autonomous agents with the ContReAct-Ollama platform. These recommendations are based on empirical testing and research into best practices for self-directed agent behavior.

## Overview

The ContReAct-Ollama platform runs autonomous agents through repeated cycles of reasoning, tool use, and reflection. Parameter tuning significantly impacts agent behavior in areas like:

- **Exploration vs. Exploitation**: How much the agent explores novel solutions vs. sticking to proven patterns
- **Tool Calling Reliability**: Accuracy in formatting tool calls and selecting appropriate tools
- **Repetition Prevention**: Avoiding loops where the agent repeats the same reasoning or actions
- **Context Management**: How well the agent maintains coherent reasoning over extended cycles

## Recommended Default Configuration

Based on analysis of successful autonomous research sessions, we recommend these defaults for general-purpose autonomous exploration:

```yaml
model_options:
  seed: 42                    # Random seed for reproducibility
  temperature: 0.6            # Balanced exploration without drift
  top_p: 0.9                  # Optimal nucleus sampling for agents
  num_predict: -1             # No token limit
  repeat_last_n: 64           # Standard look-back window
  repeat_penalty: 1.15        # Prevents repetitive loops
  num_ctx: 30000              # Large context for multi-cycle reasoning
```

### Why These Values?

**Temperature: 0.6**
- Provides balanced exploration while maintaining focus
- Previous experiments with 0.7 showed slight drift in extended sessions
- Lower than conversational agents (0.7-0.9) but higher than tool-only agents (0.2-0.3)
- Allows creative problem-solving without compromising coherence

**Top_p: 0.9**
- Research indicates 0.9 is optimal for autonomous agent token selection
- Provides diverse outputs while weighting toward high-probability tokens
- Works synergistically with temperature 0.6 for controlled exploration

**Repeat_penalty: 1.15**
- Standard range is 1.1-1.2, with 1.15 being the sweet spot
- Previous experiments with 1.1 showed occasional repetitive cycles
- Prevents loops in multi-step reasoning chains
- Still allows necessary repetition of technical terms and concepts

**Num_ctx: 30000**
- Autonomous agents benefit from large context windows
- Enables tracking extensive tool use history
- Supports long reasoning chains across multiple cycles
- Models with 30K+ context handle accumulated state better

## Use Case Specific Configurations

### High-Precision Tool Calling

For agents that primarily execute tools and need maximum reliability:

```yaml
model_options:
  temperature: 0.3            # Low randomness for consistency
  top_p: 0.85                 # Narrower token selection
  repeat_penalty: 1.05        # Allow technical term repetition
  num_ctx: 30000              # Large context still beneficial
```

**When to use:**
- Database operations and API management
- Code generation and execution
- Financial or healthcare applications
- Any scenario where tool accuracy is critical

**Trade-offs:**
- Less exploratory behavior
- More deterministic outputs
- May miss creative solutions

### Maximum Creative Exploration

For agents focused on research, brainstorming, or divergent thinking:

```yaml
model_options:
  temperature: 0.8            # Higher creativity
  top_p: 0.95                 # Broader token exploration
  repeat_penalty: 1.2         # Force diverse approaches
  num_ctx: 30000              # Support complex reasoning
```

**When to use:**
- Open-ended research tasks
- Hypothesis generation
- Creative problem-solving
- Exploring solution spaces

**Trade-offs:**
- Less predictable behavior
- May require more cycles to converge
- Higher risk of losing focus

### Conversational Interaction

For agents that primarily interact with users through natural dialogue:

```yaml
model_options:
  temperature: 0.7            # Natural language variability
  top_p: 0.9                  # Standard sampling
  repeat_penalty: 1.1         # Allow conversational patterns
  num_ctx: 30000              # Track conversation history
```

**When to use:**
- User-facing assistants
- Interactive tutoring systems
- Collaborative problem-solving
- Question-answering scenarios

**Trade-offs:**
- May be less focused on autonomous tasks
- Better for reactive than proactive behavior

## Parameter Interaction Effects

### Temperature + Top_p Combinations

The interaction between temperature and top_p is critical:

- **Low Temp (0.3) + High Top_p (0.9)**: Explores token space but weights heavily toward high probability
- **Medium Temp (0.6) + Medium Top_p (0.9)**: Balanced approach (recommended default)
- **High Temp (0.8) + Low Top_p (0.75)**: Focused creative outputs

### Repeat_penalty + Context Length

- Longer contexts benefit from higher repeat penalties
- With 30K context, use 1.15 to prevent distant loops
- With 4K context, 1.1 may be sufficient

## Model-Specific Considerations

Different Ollama models respond differently to parameters:

### Llama 3.1 and 3.2
- Well-calibrated for default recommendations
- Handle temperature up to 0.8 gracefully
- Benefit from 30K context window

### DeepSeek R1
- Excellent with reasoning tasks
- Can use slightly lower temperature (0.5-0.6)
- Strong performance with repeat_penalty 1.15

### Smaller Models (Phi-3, Gemma)
- More sensitive to high temperatures
- Recommend temperature 0.5 or lower
- May need repeat_penalty 1.2 to prevent loops

### Coding-Focused Models (CodeLlama, Qwen-Coder)
- Benefit from lower temperature (0.3-0.4)
- Use repeat_penalty 1.05 for technical terms
- Prioritize larger context windows

## Empirical Testing Results

Analysis of the gpt-oss-test-001 experiment revealed:

**Configuration Used:**
- Temperature: 0.7, Top_p: 0.9, Repeat_penalty: 1.1

**Outcomes:**
- ✅ Agent successfully conducted deep mathematical research
- ✅ Made 33 tool calls across 3 cycles
- ✅ Discovered novel patterns in Collatz Conjecture
- ⚠️ Experienced repetitive loop in Cycle 2
- ⚠️ Slight drift toward end of Cycle 3

**Recommended Adjustments:**
- Reduce temperature to 0.6 (improved focus)
- Increase repeat_penalty to 1.15 (prevent loops)

These adjustments are reflected in the updated default configuration.

## Tuning Strategy

### Systematic Approach

1. **Start Conservative**: Begin with recommended defaults
2. **Monitor Behavior**: Track tool calling accuracy, reasoning coherence, task completion
3. **Iterate Gradually**: Adjust one parameter at a time in 0.05-0.1 increments
4. **Test Across Cycles**: Run multiple cycles to observe long-term behavior
5. **Document Results**: Keep notes on parameter combinations and outcomes

### Key Metrics to Monitor

- **Tool Call Success Rate**: Percentage of correctly formatted tool calls
- **Reasoning Coherence**: Evaluate quality of thought chains
- **Exploration Diversity**: Track variety in approaches taken
- **Repetition Frequency**: Count repeated actions or reasoning loops
- **Task Completion**: Measure success rate on defined objectives

### Warning Signs

**Temperature Too High:**
- Agent loses focus on objectives
- Erratic tool selection
- Incoherent multi-cycle reasoning

**Temperature Too Low:**
- Agent gets stuck in local optima
- Repetitive approaches to problems
- Lack of creative solutions

**Repeat_penalty Too High:**
- Awkward language patterns
- Avoidance of necessary technical terms
- Forced vocabulary changes

**Repeat_penalty Too Low:**
- Repetitive cycles
- Looping reasoning patterns
- Redundant tool calls

## Advanced Techniques

### Dynamic Parameter Adjustment

Consider adjusting parameters based on cycle count:

**Early Cycles (1-3):**
- Higher temperature for exploration
- Standard repeat_penalty

**Middle Cycles (4-7):**
- Default parameters
- Balanced behavior

**Late Cycles (8+):**
- Slightly lower temperature
- Higher repeat_penalty to prevent exhaustion

### Context-Aware Tuning

As context fills up, consider:
- Reducing temperature by 0.05-0.1
- Increasing repeat_penalty slightly
- This helps maintain focus on relevant information

### Multi-Agent Systems

In systems with multiple specialized agents:
- Give each agent role-appropriate parameters
- Researcher agents: default configuration
- Tool agents: high-precision configuration
- Coordinator agents: conversational configuration

## Reproducibility

The `seed` parameter enables reproducible results:

```yaml
seed: 42  # Conventional choice, any integer works
```

**Important Notes:**
- Same seed + same parameters = same outputs (deterministically)
- Different Ollama versions may still produce variations
- Model quantization affects reproducibility
- Useful for debugging and comparative experiments

## Conclusion

Parameter tuning is an iterative process. The recommended defaults provide a solid foundation for autonomous research and exploration tasks. Adjust based on your specific use case, monitor agent behavior carefully, and document your findings to build institutional knowledge about what works best for your applications.

For questions or to share your tuning experiences, consider contributing to the project documentation or discussion forums.

## Quick Reference Table

| Use Case | Temperature | Top_p | Repeat_penalty | Context |
|----------|-------------|-------|----------------|---------|
| **Default (Research)** | 0.6 | 0.9 | 1.15 | 30000 |
| **Tool Calling** | 0.3 | 0.85 | 1.05 | 30000 |
| **Creative Exploration** | 0.8 | 0.95 | 1.2 | 30000 |
| **Conversational** | 0.7 | 0.9 | 1.1 | 30000 |
| **Code Generation** | 0.3 | 0.85 | 1.05 | 30000 |
| **Small Models** | 0.5 | 0.85 | 1.2 | 4096 |

## References

- Perplexity Research: "Optimal LLM Parameters for Autonomous Agents"
- ContReAct-Ollama Experiment Logs: gpt-oss-test-001.jsonl analysis
- Ollama Documentation: https://github.com/ollama/ollama/blob/main/docs/api.md
- Parameter tuning best practices for agent systems
