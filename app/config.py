import uuid
from langchain_core.runnables import RunnableConfig
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    llm_model:str = "deepseek-v4-flash"
    llm_timeout:int = 30

    default_user_id:str = "user001"

    database_url:str = "postgresql+psycopg://postgres:123456@localhost:5432/e-assi"

    class Config:
        env_file = ".env"

settings = Settings()

thread_id = str(uuid.uuid4())
config:RunnableConfig = {
    "configurable":
        {"thread_id": thread_id}
}