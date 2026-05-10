from langchain.agents import AgentState
from langchain.agents.middleware import before_model, after_model
from langgraph.runtime import Runtime
from agent_contexts import agent_context

# Before model hook
@before_model
def log_before_model(state: AgentState, runtime: Runtime[agent_context.Context]) -> dict | None:
    print(f"Processing request for user: {runtime.context.user_name}")
    return None

# After model hook
@after_model
def log_after_model(state: AgentState, runtime: Runtime[agent_context.Context]) -> dict | None:
    print(f"Completed request for user: {runtime.context.user_name}")
    return None