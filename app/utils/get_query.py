from app.agent.state import AgentState
from langchain_core.messages import HumanMessage
def get_user_query(state:AgentState):
    for message in reversed(state["messages"]):
        if isinstance(message,HumanMessage):
            return message.content

    return ""
