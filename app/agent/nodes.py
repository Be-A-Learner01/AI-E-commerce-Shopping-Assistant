from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage
import asyncio
from pydantic import BaseModel
from typing import Optional

model = init_chat_model(
    model="deepseek-v4-flash"
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


async def product_node(state):

    pass

