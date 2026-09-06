from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage,AIMessage,SystemMessage
from ..tools import product_search
from pydantic import BaseModel
from typing import Optional,Literal
from .state import AgentState
from ..tools.product_search import product_search
from .prompts import ANSWER_PROMPTS,REQUIREMENT_PROMPTS,MEMORY_WRITE_PROMPTS,CONFLICT_PROMPTS
from app.memory.long_term.repository import (search_memories,create_memory,find_similar_memories,is_duplicate,update_memory)
from app.memory.long_term.postgres import SessionLocal

model = init_chat_model(
    model="deepseek-v4-flash",
    temperature =0,
    extra_body={
        "thinking": {
            "type": "disabled"
        }
    }
)

class MemoryExtraction(BaseModel):
    memory_save:bool
    user_id:str
    content:Optional[str] = None
    memory_type:Optional[str] = None
    importance:Optional[float] = None

class MemoryConflict(BaseModel):
    conflict:Literal["yes","no"]
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

memory_model = model.with_structured_output(MemoryExtraction)

conflict_model = model.with_structured_output(MemoryConflict)

requirement_model = model.with_structured_output(Requirements)

async def memory_retrieval_node(state:AgentState):
    user_id = "user_001"
    db = SessionLocal()
    query = state["query"]

    memories =  search_memories(
        db=db,
        user_id=user_id,
        query=query,
        top_k=5
    )
    print(memories)
    return {
        "memories":[memory.content for memory in memories]
    }

async def detect_memory_conflict(existing_memory:str,new_memory:str) -> bool:

    prompts = CONFLICT_PROMPTS.format(
        existing_memory=existing_memory,
        new_memory=new_memory

    )
    resposne = await conflict_model.ainvoke(
        [
            SystemMessage(content=prompts)
        ]
    )
    return resposne.conflict == "yes"


async def memory_write_node(state:AgentState):
    user_id ="test001"
    messages = state["messages"]
    response = await memory_model.ainvoke(
        [
            SystemMessage(content=MEMORY_WRITE_PROMPTS),
            *messages
        ]
    )
    if not response.memory_save or not response.content:
        return {}
    db = SessionLocal()
    similar_memories = find_similar_memories(db=db,user_id=user_id,query=response.content,top_k=1)

    try:
        dedup =is_duplicate(similar_memories)
        if dedup:
            return {}
        if similar_memories:
            existing_memory, distance = similar_memories[0]
            conflict = await detect_memory_conflict(existing_memory=existing_memory.content,new_memory=response.content)
            print("conflict:", conflict if similar_memories else None)
            if conflict:
                update_memory(
                    db=db,
                    memory_id=existing_memory.memory_id,
                    content=response.content,
                    memory_type=response.memory_type,
                    importance = response.importance
                )
                return {}

        create_memory(
            db=db,
            user_id=user_id,
            content=response.content,
            memory_type=response.memory_type,
            importance=response.importance
        )
        print("=== Memory Debug ===")
        print("new memory:", response.content)
        print("similar memories:", similar_memories)
        print("dedup:", dedup)

        return {}
    finally:
        db.close()

async def requirement_node(state:AgentState):
    messages = state["messages"]
    memories = state["memories"]
    memory_text = "\n".join(f"{memory}" for memory in memories)
    response = await requirement_model.ainvoke(
        [
        SystemMessage(content=REQUIREMENT_PROMPTS),
        HumanMessage(content=f"""
    以下是当前用户相关的长期记忆：
    {memory_text}
    """),
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

