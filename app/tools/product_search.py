from app.retrieval.reranker import rerank_results
from langsmith import traceable
from app.agent.state import AgentState
import asyncio

@traceable(name="product_search")
def product_search(state):
    results = rerank_results(state)

    return results

async def search_with_retry(state:AgentState):
    max_retries = 2

    for attempt in range(max_retries + 1):
        try:
            return product_search(state)

        except Exception as e:
            print(f"=== Product Search Error ===")
            print(f"attempt: {attempt + 1}")
            print(f"error: {e}")

            if attempt == max_retries:
                return None

            await asyncio.sleep(1)