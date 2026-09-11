import asyncio
from app.config import settings
from utils.exceptions import LLMError


async def invoke_llm_with_timeout(model,messages):
    try:
        return await asyncio.wait_for(
            model.ainvoke(messages),
            timeout=settings.llm_timeout
        )
    except asyncio.TimeoutError as e:
        raise LLMError(
            f"LLM request timeout after{settings.llm_timeout}"
        ) from e

    except Exception as e:
        raise LLMError(
            f":LLM request failed:{e}"
        ) from e