from sentence_transformers import CrossEncoder
from .hybrid_search import hybrid_search
from langsmith import traceable
from app.utils.text_converter import dict_to_text
import time

model = CrossEncoder("BAAI/bge-reranker-v2-m3")
def rerank(state,documents,k = 5):
    pairs = []

    requirements = dict_to_text(state["requirements"])

    for doc in documents:
        pairs.append(
            (requirements,doc.page_content)
        )
    start = time.perf_counter()
    scores = model.predict(pairs,batch_size=5)
    elapsed = time.perf_counter() - start
    print(f"=== Latency === reranker predict: {elapsed:.2f}s")

    ranked = sorted(
        zip(documents,scores),
        key = lambda x:x[1],
        reverse = True
    )

    return [
        {"document":doc,"rerank_score":float(score)}
        for doc,score in ranked[:k]
    ]
@traceable(name="rerank")
def rerank_results(state):

    hybrid_results = hybrid_search(state,k = 5)
    return [
        {
            "document": item["documents"],
            "rerank_score": item["rrf_score"],
        }
        for item in hybrid_results
    ]
# documents = [item["documents"] for item in hybrid_results]
# return rerank(state,documents)