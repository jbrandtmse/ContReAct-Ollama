"""
Debug why llama3.1:8b returns empty content with our system prompt.
"""

import ollama
from contreact_ollama.tools.tool_dispatcher import ToolDispatcher
from contreact_ollama.tools.memory_tools import MemoryTools
from contreact_ollama.constants import SYSTEM_PROMPT

# Initialize tools to get definitions
memory_tools = MemoryTools(db_path="data/memory.db", run_id="debug-test")
tool_dispatcher = ToolDispatcher(memory_tools=memory_tools)
tools = tool_dispatcher.get_tool_definitions()

# Build system prompt with tool definitions
from contreact_ollama.llm.prompt_assembler import build_prompt
from contreact_ollama.state.agent_state import AgentState

# Create minimal agent state
agent_state = AgentState(
    run_id="debug-test",
    cycle_number=1,
    model_name="llama3.1:8b",
    message_history=[],
    reflection_history=[]
)

# Build prompt
messages = build_prompt(
    agent_state=agent_state,
    system_prompt=SYSTEM_PROMPT,
    tool_definitions=tools,
    diversity_feedback=None
)

print("Testing llama3.1:8b with actual system prompt...")
print("=" * 60)

client = ollama.Client(host="http://192.168.0.123:11434")

response = client.chat(
    model="llama3.1:8b",
    messages=messages,
    tools=tools,
    options={"temperature": 0.7}
)

print("\nResponse structure:")
print(f"Type: {type(response)}")
print(f"\nMessage role: {response.message.role}")
print(f"Message content: '{response.message.content}'")
print(f"Message content is None: {response.message.content is None}")
print(f"Message content length: {len(response.message.content) if response.message.content else 0}")

print(f"\nTool calls present: {hasattr(response.message, 'tool_calls') and response.message.tool_calls is not None}")

if hasattr(response.message, 'tool_calls') and response.message.tool_calls:
    print(f"Tool calls: {response.message.tool_calls}")
    for tc in response.message.tool_calls:
        print(f"  - {tc.function.name}({tc.function.arguments})")
else:
    print("No tool calls in response")

print("\n" + "=" * 60)
print("DIAGNOSIS:")
if response.message.content is None and hasattr(response.message, 'tool_calls') and response.message.tool_calls:
    print("✓ Model is returning tool_calls with None content (EXPECTED for tool calling)")
elif response.message.content == "":
    print("✗ Model returning empty string (UNEXPECTED)")
elif response.message.content:
    print(f"✓ Model returning content: {response.message.content[:100]}...")
else:
    print("✗ Unknown response state")
