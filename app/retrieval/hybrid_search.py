from collections import defaultdict
from .vector_search import semantic_search
from .bm25_search import bm25_search
from langsmith import traceable

def reciprocal_rank_fusion(semantic_results,bm25_results,k = 60):
    scores = defaultdict(float)
    documents = {}
    for rank,doc in enumerate(semantic_results,start=1):
        doc_id = doc.metadata["id"]
        scores[doc_id] += 1 / (k + rank)
        documents[doc_id] = doc
    for rank,doc in enumerate(bm25_results,start=1):
        doc_id = doc.metadata["id"]
        scores[doc_id] +=1 / (k + rank)
        documents[doc_id] = doc

    ranked = sorted(
        scores.items(),
        key=lambda  x:x[1],
        reverse=True,
    )
    return [
        {
            "id":doc_id,
            "documents":documents[doc_id],
            "rrf_score":score
        }
        for doc_id,score in ranked
    ]

@traceable(name="hybrid_search")
def hybrid_search(state,k:int = 10):
    semantic_results = semantic_search(state)
    bm25_results = bm25_search(state)
    results = reciprocal_rank_fusion(
        semantic_results,
        bm25_results
    )
    return results[:k]