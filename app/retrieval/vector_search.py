from ..data.vector_store import vector_store
from langsmith import traceable
from app.utils.text_converter import dict_to_text
import time
@traceable(name="semantic_search")
def semantic_search(state,k:int = 20):
    start = time.perf_counter()
    requirements =dict_to_text(state["requirements"])
    results = vector_store.similarity_search(requirements,k)

    elapsed = time.perf_counter() - start
    print(f"=== Latency === semantic_search: {elapsed:.2f}s")

    return results