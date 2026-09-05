from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage,AIMessage,SystemMessage
from ..tools import product_search
from pydantic import BaseModel
from typing import Optional
from .state import AgentState
from ..tools.product_search import product_search
from .prompts import ANSWER_PROMPTS,REQUIREMENT_PROMPTS

model = init_chat_model(
    model="deepseek-v4-flash",
    temperature =0,
    extra_body={
        "thinking": {
            "type": "disabled"
        }
    }
)

class Requirements(BaseModel):
    category:str
    brand:Optional[str] = None
    description:Optional[str] = None
    price_max:Optional[float] = None
    price_min:Optional[float] = None
    price_preference: Optional[str] = None
    sizes:Optional[str] = None
    storage:Optional[str] = None
    color:Optional[list[str]] = None
    tags:Optional[list[str]] = None


structured_model = model.with_structured_output(Requirements)

async def requirement_node(state):
    messages = state["messages"]
    response = await structured_model.ainvoke(
        [
        SystemMessage(content=REQUIREMENT_PROMPTS),
        *messages,
        ]
    )
    return {"requirements":response.model_dump()}


async def product_node(state:AgentState):
    products = product_search(state)
    return {"products":products}

async def answer_node(state:AgentState):
    messages = state["messages"]

    answer_prompt = ANSWER_PROMPTS
    context = f"""
    当前用户需求：{state["query"]}
    
    结构化需求：{state["requirements"]}

    商品搜索结果：{state["products"]}
    """
    answer = await model.ainvoke(
        [SystemMessage(content=answer_prompt),
         *messages,
         HumanMessage(content=context)]
    )

    return {
        "answer": answer.content,
        "messages":[
            AIMessage(content=answer.content)
        ]
    }

