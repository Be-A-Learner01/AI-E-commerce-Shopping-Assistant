
from ..retrieval.bm25_search import bm25_search

def product_search(state):
    results = bm25_search(state)
    return results
