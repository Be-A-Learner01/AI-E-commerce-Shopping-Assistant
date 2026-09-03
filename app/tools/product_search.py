from langchain.tools import tool
from app.retrieval.bm25_search import bm25_search


@tool
async def product_search(state):
    results = bm25_search(state)
    return results
