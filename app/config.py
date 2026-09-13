import uuid
from langchain_core.runnables import RunnableConfig
from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    llm_model:str = "deepseek-v4-flash"
    llm_timeout:int = 30

    default_user_id:str = "user001"

    database_url:str = "postgresql+psycopg://postgres:123456@localhost:5432/e-assi"

    langsmith_tracing: bool = False
    langsmith_api_key: str | None = None
    langsmith_project: str | None = None
    langsmith_endpoint: str | None = None

    model_config = SettingsConfigDict(env_file = ".env",extra="ignore")


settings = Settings()

thread_id = str(uuid.uuid4())

config:RunnableConfig = {
    "configurable":
        {"thread_id": thread_id}
}