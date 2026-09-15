from langchain.chat_models import init_chat_model
from app.schemas.memory_schema import MemoryConflict,MemoryExtraction
from app.schemas.requirement_schema import Requirements
import asyncio
from app.config import settings
from app.utils.exceptions import LLMError,RETRYABLE_EXCEPTIONS
from app.utils.loggings import logger
from app.tools import TOOLS

model = init_chat_model(
    model=settings.llm_model,
    temperature =0,
    extra_body={
        "thinking": {
            "type": "disabled"
        }
    }
)
memory_model = model.with_structured_output(MemoryExtraction)

conflict_model = model.with_structured_output(MemoryConflict)

requirement_model = model.with_structured_output(Requirements)

llm_with_tools = model.bind_tools(TOOLS)

async def invoke_llm_with_timeout(model,messages):
    logger.info(">>> invoke_llm_with_timeout START")
    try:
        logger.info(">>> LLM messages: %r", messages)
        response = await asyncio.wait_for(
            model.ainvoke(messages),
            timeout=settings.llm_timeout
        )
        logger.info("LLM raw response:%r",response)

        if response is not None:
            logger.info(">>> response type: %s", type(response))
            logger.info(">>> response content: %r", getattr(response, "content", None))
            logger.info(">>> response tool_calls: %r", getattr(response, "tool_calls", None))
            logger.info(
                ">>> response additional_kwargs: %r",
                getattr(response, "additional_kwargs", None),
            )

        if response is None:
            raise LLMError("LLM returned None")

        return response
    except asyncio.TimeoutError as e:
        raise TimeoutError(
            f"LLM request timeout after {settings.llm_timeout}s"
        ) from e

    except LLMError:
        raise

    except RETRYABLE_EXCEPTIONS:
        raise

    except Exception as e:
        raise LLMError(
            f":LLM request failed:{e}"
        ) from e