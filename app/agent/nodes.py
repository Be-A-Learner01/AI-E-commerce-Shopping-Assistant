from models.llm import model,memory_model,requirement_model
from utils.llm import invoke_llm_with_timeout
from langchain.messages import HumanMessage,AIMessage,SystemMessage
from .state import AgentState
from .prompts import ANSWER_PROMPTS,REQUIREMENT_PROMPTS,MEMORY_WRITE_PROMPTS
from app.memory.long_term.repository import search_memories
from app.memory.long_term.postgres import SessionLocal
from memory.long_term.service import save_memory
from tools.product_search import search_with_fallback
from app.config import settings
from utils.loggings import logger
from utils.retry import retry_async


async def memory_retrieval_node(state:AgentState):
    db = SessionLocal()
    user_id = state.get("user_id",settings.default_user_id)

    try:
        query = state["query"]

        logger.info("Memory retrieval started")

        memories =  search_memories(
            db=db,
            user_id=user_id,
            query=query,
            top_k=5
        )

        logger.info("Memory retrieval completed")

        return {
            "memories":[memory.content for memory,distance in memories]
        }

    except Exception:
        logger.exception("Memory retrieval failed")
        raise
    finally:
        db.close()

async def requirement_node(state:AgentState):
    messages = state["messages"]

    memories = state["memories"]


    memory_text = "\n".join(f"{memory}" for memory in memories)
    try:
        logger.info("Requirement extraction stared")

        response = await retry_async(
            invoke_llm_with_timeout,
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
        logger.info("Requirement LLM response: %s", response)

        if response is None:
            logger.warning("Requirement extraction return None")
            raise ValueError("Requirement extraction return None")

        requirements = response.model_dump()

        logger.info("Requirement extraction completed")

        return {"requirements": requirements}
    except Exception:
        logger.exception("Requirement extraction failed")
        raise

async def product_node(state:AgentState):
    try:
        logger.info("Products search started")

        result = await search_with_fallback(state)

        if result is None:

            return {
                "products": [],
                "error": "商品搜索超时，请稍后重试"
            }

        logger.info("Products search completed: %d products found",len(result))

        return {"products":result}

    except Exception:
        logger.exception("Products search failed")
        raise

async def memory_write_node(state:AgentState):
    user_id = state.get("user_id",settings.default_user_id)

    messages = state["messages"]
    try:
        logger.info("Memory write started")

        response = await retry_async(
            invoke_llm_with_timeout,
            memory_model,
            [
                SystemMessage(content=MEMORY_WRITE_PROMPTS),
                *messages
            ]
        )

        if not response.memory_save or not response.content:
            logger.info("Memory write skipped")
            return {}

        results = await save_memory(
            user_id=user_id,
            content=response.content,
            memory_type=response.memory_type,
            importance=response.importance
        )

        logger.info(
            "Memory write completed: action=%s",
            results["action"]
        )
        return {}

    except Exception:
        logger.exception("Memory write failed")
        raise

async def answer_node(state:AgentState):
    try:
        logger.info("Answer generation started")

        if state.get("error"):
            logger.warning("Answer generation skipped due to previous error")
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

        answer = await retry_async(
            invoke_llm_with_timeout,
            model,
            [SystemMessage(content=answer_prompt),
             *messages,
             HumanMessage(content=context)]
        )
        logger.info("Answer generation completed")

        return {
            "answer": answer.content,
            "messages":[
                AIMessage(content=answer.content)
            ]
        }
    except Exception:
        logger.exception("Answer generation failed")
        raise

