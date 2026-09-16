from langgraph.graph import MessagesState
from app.schemas.requirement_schema import Requirements

class AgentState(MessagesState):
    #用户名
    user_id:str
    #历史记忆
    memories:list[str]
    #根据用户的需求产生的结果
    requirements: Requirements
    #符合用户需求的产品
    products:list[dict]
    # HITL 用户确认结果
    human_confirmation: str | None
    #回答
    answer:str
    #错误
    error:str | None
