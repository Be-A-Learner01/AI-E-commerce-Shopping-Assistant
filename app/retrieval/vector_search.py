from ..data.vector_store import vector_store
from langsmith import traceable
from app.utils.text_converter import dict_to_text
@traceable(name="semantic_search")
def semantic_search(state,k:int = 20):
    requirements =dict_to_text(state["requirements"])
    results = vector_store.similarity_search(requirements,k)
    return results