from typing import TypedDict
class AgentState(TypedDict):
    #用户的问题
    query:str
    #根据用户的需求产生的结果
    requirements: dict[str,object]
    #符合用户需求的产品
    products:list[dict]
    #回答
    answer:str
