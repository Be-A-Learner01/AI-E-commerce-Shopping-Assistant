import asyncio
from app.config import settings

async def invoke_llm_with_timeout(model,messages):

    return await asyncio.wait_for(
        model.ainvoke(messages),
        timeout=settings.llm_timeout
    )