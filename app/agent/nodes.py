from app.models.llm import model,memory_model,requirement_model,invoke_llm_with_timeout,llm_with_tools
from langchain.messages import HumanMessage,AIMessage,SystemMessage
from app.utils.exceptions import ProductSearchError,MemoryError,LLMError
from app.agent.state import AgentState
from app.agent.prompts import ANSWER_PROMPT,REQUIREMENT_PROMPT,MEMORY_WRITE_PROMPT,AGENT_PROMPT
from app.memory.long_term.repository import search_memories
from app.memory.long_term.postgres import SessionLocal
from app.memory.long_term.service import save_memory
from app.tools.product_search import search_with_fallback
from app.config import settings
from app.utils.loggings import logger
from app.utils.retry import retry_async
from app.utils.get_query import get_user_query


async def memory_retrieval_node(state:AgentState):
    db = SessionLocal()

    user_id = state.get("user_id",settings.default_user_id)

    query = get_user_query(state)

    try:
        logger.info("Memory retrieval started")

        memories = search_memories(
            db=db,
            user_id=user_id,
            query=query,
            top_k=5
        )

        logger.info("Memory retrieval completed")

        return {
            "memories":[memory.content for memory,distance in memories]
        }

    except Exception as e:
        logger.exception("Memory retrieval failed")
        raise MemoryError(
            f"Memory retrieval failed: {e}"
        ) from e
    finally:
        db.close()

async def requirement_node(state:AgentState):
    messages = state["messages"]

    memories = state["memories"]

    current_user_message = next(
        message
        for message in reversed(messages)
        if isinstance(message, HumanMessage)
    )

    memory_text = "\n".join(f"{memory}" for memory in memories)
    print("========== MEMORY INPUT ==========")
    print(memories)

    try:
        logger.info("Requirement extraction stared")

        response = await retry_async(
            invoke_llm_with_timeout,
            requirement_model,
            [
            SystemMessage(content=REQUIREMENT_PROMPT),
            HumanMessage(content=f"""
                以下是当前用户相关的长期记忆：
                {memory_text}
                当前用户需求：
                {current_user_message.content}
                """),
            ]
        )
        logger.info("Requirement LLM response: %s", response)

        if response is None:
            logger.warning("Requirement extraction return None")
            raise LLMError("Requirement extraction returned None")

        requirements = response.model_dump()

        print("\n========== REQUIREMENTS ==========")
        print(requirements)

        for key, value in requirements.items():
            if value == "null":
                requirements[key] = None

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
            logger.warning("Product search returned None")
            return {
                "products": [],
                "error": "商品搜索超时，请稍后重试"
            }

        logger.info("Products search completed: %d products found",len(result))

        return {"products":result}

    except Exception as e:
        logger.exception("Products search failed")
        raise ProductSearchError(
            f"Memory retrieval failed: {e}"
        ) from e

async def answer_node(state: AgentState):
    try:
        logger.info("Answer generation started")

        if state.get("error"):
            logger.warning("Answer generation skipped due to previous error")
            return {
                "answer": state["error"],
                "messages": [
                    AIMessage(content=state["error"])
                ]
            }

        messages = state["messages"]
        query = get_user_query(state)

        answer_prompt = ANSWER_PROMPT
        context = f"""
        当前用户需求：{query}

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
            "messages": [
                AIMessage(content=answer.content)
            ]
        }
    except Exception:
        logger.exception("Answer generation failed")
        raise

async def memory_write_node(state:AgentState):
    user_id = state.get("user_id",settings.default_user_id)

    messages = state["messages"]

    current_user_message = next(
        message
        for message in reversed(messages)
        if isinstance(message, HumanMessage)
    )

    try:
        logger.info("Memory write started")

        response = await retry_async(
            invoke_llm_with_timeout,
            memory_model,
            [
                SystemMessage(content=MEMORY_WRITE_PROMPT),
                current_user_message
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

async def agent_node(state: AgentState):
    messages = state["messages"]
    requirements = state["requirements"]
    context = SystemMessage(
        content=f"""
    当前用户已经提取出的结构化购物需求：

    {requirements}

    请基于这些需求决定是否调用工具。

    如果需要搜索商品，调用 search_products，并使用上述 requirements。
    """
    )

    response = await retry_async(
        invoke_llm_with_timeout,
        llm_with_tools,
        [
            SystemMessage(content=AGENT_PROMPT),
            context,
            *messages
        ],
    )

    return {"messages": [response]}


