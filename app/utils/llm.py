import asyncio
from app.config import settings
from utils.exceptions import LLMError
from utils.loggings import logger


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
        raise LLMError(
            f"LLM request timeout after{settings.llm_timeout}"
        ) from e

    except LLMError:
        raise

    except Exception as e:
        raise LLMError(
            f":LLM request failed:{e}"
        ) from e