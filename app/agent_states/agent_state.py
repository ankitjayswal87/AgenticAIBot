from langchain.agents import AgentState

class CustomState(AgentState):
    user_id: str
    booking_status: str