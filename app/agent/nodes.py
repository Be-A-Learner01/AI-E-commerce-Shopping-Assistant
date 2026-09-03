from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage
import asyncio
from ..tools import product_search
from pydantic import BaseModel
from typing import Optional
from .state import AgentState
from ..tools.product_search import product_search
from .prompts import ANSWER_PROMPTS
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
    prompt = ANSWER_PROMPTS.format(
        query = state["query"],
        requirements = state["requirements"],
        products = state["products"],
    )
    answer = await model.ainvoke([
        HumanMessage(content=prompt)
    ])

    return {
        "answer": answer.content
    }

