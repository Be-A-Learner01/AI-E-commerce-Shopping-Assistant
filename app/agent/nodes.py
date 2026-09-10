from models.llm import model,memory_model,requirement_model
from utils.llm import invoke_llm_with_timeout
from langchain.messages import HumanMessage,AIMessage,SystemMessage
from .state import AgentState
from .prompts import ANSWER_PROMPTS,REQUIREMENT_PROMPTS,MEMORY_WRITE_PROMPTS
from app.memory.long_term.repository import search_memories
from app.memory.long_term.postgres import SessionLocal
from memory.long_term.service import save_memory
from tools.product_filter import has_matching_product
from tools.product_search import search_with_retry
from app.config import settings


async def memory_retrieval_node(state:AgentState):
    db = SessionLocal()
    user_id = state.get("user_id",settings.default_user_id)

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

        return {
            "memories":[memory.content for memory,distance in memories]
        }

    finally:
        db.close()

async def memory_write_node(state:AgentState):
    user_id = state.get("user_id",settings.default_user_id)

    messages = state["messages"]

    response = await invoke_llm_with_timeout(
        memory_model,
        [
            SystemMessage(content=MEMORY_WRITE_PROMPTS),
            *messages
        ]
    )

    if not response.memory_save or not response.content:
        return {}

    results = await save_memory(
        user_id=user_id,
        content=response.content,
        memory_type=response.memory_type,
        importance=response.importance
    )
    print("=== Memory Action ===")
    print(results["action"])

    return {}

async def requirement_node(state:AgentState):

    messages = state["messages"]

    memories = state["memories"]

    memory_text = "\n".join(f"{memory}" for memory in memories)

    response = await invoke_llm_with_timeout(
        requirement_model,
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

    products = await search_with_retry(state)

    if products is None:
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

    answer = await invoke_llm_with_timeout(
        model,
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

