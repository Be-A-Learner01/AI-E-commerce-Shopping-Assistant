from app.models.llm import memory_model,requirement_model,invoke_llm_with_timeout,llm_with_tools
from langchain.messages import HumanMessage,SystemMessage
from app.utils.exceptions import MemoryError,LLMError
from app.agent.state import AgentState
from app.agent.prompts import REQUIREMENT_PROMPT,MEMORY_WRITE_PROMPT,AGENT_PROMPT
from app.memory.long_term.repository import search_memories
from app.memory.long_term.postgres import SessionLocal
from app.memory.long_term.service import save_memory
from app.config import settings
from app.utils.loggings import logger
from app.utils.retry import retry_async
from app.utils.get_query import get_user_query


async def memory_retrieval_node(state:AgentState):

    user_id = state.get("user_id",settings.default_user_id)

    query = get_user_query(state)

    try:
        logger.info("Memory retrieval started")

        db = SessionLocal()
        
        try:
            memories = search_memories(
                db=db,
                user_id=user_id,
                query=query,
                top_k=5,
                threshold=0.6
            )

            memory_contents = [
                memory.content
                for memory, distance in memories
            ]

            for memory, distance in memories:
                logger.info(
                    "Memory retrieved: %s | similarity=%.4f",
                    memory.content,
                    1 - distance
                )

            logger.info(
                "Memory retrieval completed: %d memories",
                len(memory_contents)
            )

            return {
                "memories": memory_contents
            }
        finally:
            db.close()

    except Exception as e:
        logger.exception("Memory retrieval failed")
        raise MemoryError(
            f"Memory retrieval failed: {e}"
        ) from e

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

        logger.info("Requirement extraction completed")

        return {"requirements": requirements}

    except Exception:
        logger.exception("Requirement extraction failed")
        raise

async def memory_write_node(state:AgentState):
    user_id = state.get("user_id",settings.default_user_id)
    print(user_id)
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


