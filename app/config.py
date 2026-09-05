import uuid
from langchain_core.runnables import RunnableConfig


thread_id = str(uuid.uuid4())
config:RunnableConfig = {
    "configurable":
        {"thread_id": thread_id}
}