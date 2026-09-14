import asyncio
from app.utils.loggings import logger
from app.utils.exceptions import RETRYABLE_EXCEPTIONS,LLMError

async def retry_async(func,*args,max_retries=2,**kwargs):
    func_name = getattr(func,"__name__",str(func))
    for attempt in range(max_retries + 1):
        try:
            result = await func(*args,**kwargs)

            if result is None:

                raise LLMError("Function returned None")

            return result

        except RETRYABLE_EXCEPTIONS as e:

            if attempt == max_retries:

                logger.exception("%s failed after %d retries",func_name,max_retries)
                raise

            wait_time = 2 ** attempt

            logger.warning(
                "Retrying %s | attempt=%d/%d | error=%s",
                func_name,
                attempt + 1,
                max_retries,
                e
            )
            await asyncio.sleep(wait_time)

        except Exception:
            logger.exception(
                "%s failed with non-retryable error",
                func_name
            )
            raise