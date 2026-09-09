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
import asyncio
import time
model = init_chat_model(
    model="deepseek-v4-flash",
    temperature =0,
    extra_body={
        "thinking": {
            "type": "disabled"
        }
    }
)
LLM_TIMEOUT = 30
BRAND_MAP = {
    "苹果": "Apple",
    "三星": "Samsung",
    "华为": "Huawei",
    "小米": "Xiaomi",
    "索尼": "Sony",
}
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

async def invoke_llm_with_timeout(model,messages):

    return await asyncio.wait_for(
        model.ainvoke(messages),
        timeout=LLM_TIMEOUT
    )

async def memory_retrieval_node(state:AgentState):
    start =time.perf_counter()
    db = SessionLocal()
    user_id = "test001"

    try:
        query = state["query"]
        memories =  search_memories(
            db=db,
            user_id=user_id,
            query=query,
            top_k=5
        )
        for memory,distance in memories:
            print(f"content:{memory.content}")
            print(f"distance:{distance}")
        elapsed = time.perf_counter() - start
        print(f"=== LLM Latency === conflict: {elapsed:.2f}s")
        return {
            "memories":[memory.content for memory,distance in memories]
        }

    finally:
        db.close()

async def detect_memory_conflict(existing_memory:str,new_memory:str) -> bool:

    prompts = CONFLICT_PROMPTS.format(
        existing_memory=existing_memory,
        new_memory=new_memory

    )
    start = time.perf_counter()
    resposne = await invoke_llm_with_timeout(
        conflict_model,
        [
            SystemMessage(content=prompts)
        ]
    )
    elapsed = time.perf_counter() - start
    print(f"=== LLM Latency === conflict: {elapsed:.2f}s")
    return resposne.conflict == "yes"


async def memory_write_node(state:AgentState):
    user_id ="test001"
    messages = state["messages"]
    start = time.perf_counter()
    response = await invoke_llm_with_timeout(
        memory_model,
        [
            SystemMessage(content=MEMORY_WRITE_PROMPTS),
            *messages
        ]
    )
    elapsed = time.perf_counter() - start
    print(f"=== LLM Latency === memory_write: {elapsed:.2f}s")
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
    start = time.perf_counter()
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
    elapsed = time.perf_counter() - start
    print(f"=== LLM Latency === requirement: {elapsed:.2f}s")
    return {"requirements":response.model_dump()}

def has_matching_product(products, requirements):
    expected_brand = requirements.get("brand")

    if expected_brand:
            expected_brand = BRAND_MAP.get(
                expected_brand,
                expected_brand
            )

    for item in products:
        product = item["document"].metadata["product"]

        if expected_brand:
            if product["brand"] != expected_brand:
                continue

        if requirements.get("price_max") is not None:
            if product["price"] > requirements["price_max"]:
                continue

        if requirements.get("price_min") is not None:
            if product["price"] < requirements["price_min"]:
                continue

        return True

    return False

async def product_node(state:AgentState):

    products = await  search_with_retry(state)

    if products is  None:
        return {
            "products":[],
            "error":"商品搜索超时，请稍后重试"
        }

    requirements = state["requirements"]

    if not has_matching_product(products,requirements):
        print("=== Product Search Fallback ===")

        fallback_state = state.copy()
        fallback_requirements = state["requirements"].copy()

        fallback_requirements["color"] =None
        fallback_requirements["sizes"] = None
        fallback_requirements["storage"] = None

        fallback_state["requirements"] = fallback_requirements

        products = await search_with_retry(fallback_state)
        if products is None:
            return {
                "products":[],
                "error": "商品搜索超时，请稍后重试"
            }
    return {"products":products}

async def search_with_retry(state:AgentState):
    max_retries = 4

    for attempt in range(max_retries + 1):
        try:
            return product_search(state)

        except Exception as e:
            print(f"=== Product Search Error ===")
            print(f"attempt: {attempt + 1}")
            print(f"error: {e}")

            if attempt == max_retries:
                return None

            await asyncio.sleep(1)

async def answer_node(state:AgentState):

    if state.get("error"):
        return {
            "answer":state["error"],
            "messages":[
                AIMessage(content=state["error"])
            ]
        }

    messages = state["messages"]

    answer_prompt = ANSWER_PROMPTS
    context = f"""
    当前用户需求：{state["query"]}
    
    结构化需求：{state["requirements"]}

    商品搜索结果：{state["products"]}
    """
    start = time.perf_counter()
    answer = await invoke_llm_with_timeout(
        model,
        [SystemMessage(content=answer_prompt),
         *messages,
         HumanMessage(content=context)]
    )
    elapsed = time.perf_counter() - start
    print(f"=== LLM Latency === answer: {elapsed:.2f}s")

    return {
        "answer": answer.content,
        "messages":[
            AIMessage(content=answer.content)
        ]
    }

