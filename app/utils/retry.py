import asyncio
from utils.loggings import logger
from utils.exceptions import RETRYABLE_EXCEPTIONS

async def retry_async(func,*args,max_retries=2,**kwargs):
    for attempt in range(max_retries + 1):
        try:
            return await func(*args,**kwargs)

        except RETRYABLE_EXCEPTIONS as e:
            if attempt == max_retries:
                logger.exception("Failed after retries")
                raise

            wait_time = 2 ** attempt

            logger.warning(
                "Retrying %s | attempt=%d/%d | error=%s",
                func.__name__,
                attempt + 1,
                max_retries,
                wait_time,
                e
            )
            await asyncio.sleep(wait_time)

        except Exception:
            logger.exception(
                "%s failed with non-retryable error",
                func.__name__
            )
            raise