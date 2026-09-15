from app.agent.state import AgentState
from langchain_core.messages import HumanMessage
def get_user_query(state:AgentState):
    messages = state["messages"]

    user_messages = [
        message.content
        for message in messages
        if isinstance(message, HumanMessage)
    ]

    if not user_messages:
        return ""

    recent_messages = user_messages[-3:]

    return "\n".join(recent_messages)