from langchain.chat_models import init_chat_model
from schemas.memory_schema import MemoryConflict,MemoryExtraction
from schemas.requirement_schema import Requirements
from app.config import settings


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