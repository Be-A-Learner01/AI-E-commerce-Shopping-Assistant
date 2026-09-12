from sqlalchemy.exc import OperationalError
import httpx

class BaseError(Exception):
    """项目基础异常"""
    pass

class LLMError(BaseError):
    """LLM 相关错误"""
    pass

class MemoryError(BaseError):
    """长期记忆相关错误"""
    pass

RETRYABLE_EXCEPTIONS = (
    httpx.TimeoutException,
    httpx.ConnectError,
    OperationalError,
    ConnectionError,
    TimeoutError,
    LLMError,
)