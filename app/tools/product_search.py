from app.retrieval.reranker import rerank_results
from langsmith import traceable

@traceable(name="product_search")
def product_search(state):
    results = rerank_results(state)

    return results
