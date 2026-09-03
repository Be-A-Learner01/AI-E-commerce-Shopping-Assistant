from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage
import asyncio
from ..tools import product_search
from pydantic import BaseModel
from typing import Optional
from .state import AgentState
from ..tools.product_search import product_search
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
    brand:Optional[str]=None
    description:Optional[str]=None
    price_max:Optional[float]=None
    price_min:Optional[float]=None


structured_model = model.with_structured_output(Requirements)

async def requirement_node(state):
    response = await structured_model.ainvoke(
        [
        HumanMessage(
            content=state["query"]
            )
        ]
    )
    return {"requirements":response.model_dump()}


async def product_node(state:AgentState):
    products = product_search(state)
    return {"products":products}

async def answer_node(state: AgentState):
    prompt = f"""
你是一个电商购物助手。

用户需求：
{state["query"]}

提取出的需求：
{state["requirements"]}

搜索到的商品：
{state["products"]}

请根据搜索结果回答用户。
要求：
1. 只推荐搜索结果中的商品，不要编造商品。
2. 简单说明为什么这些商品符合用户需求。
3. 如果搜索结果不完全符合需求，要诚实说明。
4. 回答简洁、自然。
"""
    answer = await model.ainvoke([
        HumanMessage(content=prompt)
    ])

    return {
        "answer": answer.content
    }

