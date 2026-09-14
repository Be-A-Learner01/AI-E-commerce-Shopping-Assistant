from app.retrieval.reranker import rerank_results
from langsmith import traceable
from app.utils.loggings import logger
from .product_filter import filter_products
from app.utils.retry import retry_async
from langchain_core.tools import tool
from typing import TYPE_CHECKING
from app.agent.state import AgentState

@traceable(name="product_search")
async def product_search(state:AgentState):

    results = rerank_results(state)

    return results

async def search_with_retry(state:AgentState):

    result = await retry_async(product_search,state)

    return result

@traceable(name="search_with_fallback")
async def search_with_fallback(state:AgentState):
    products = await search_with_retry(state)

    if products is None:
        logger.warning("Products search timeout")
        return None

    requirements = state["requirements"]

    for item in products:
        product = item["document"].metadata["product"]
        print(
            "RAW PRODUCT:",
            product["name"],
            "| category:", product.get("category"),
            "| brand:", product.get("brand"),
            "| price:", product.get("price")
        )

    filtered_products = filter_products(products,requirements)

    if filtered_products:
        return filtered_products

    logger.warning("Search fallback started")

    fallback_state = state.copy()
    fallback_requirements = requirements.copy()
    fallback_requirements["color"] =None
    fallback_requirements["sizes"] = None
    fallback_requirements["storage"] = None
    fallback_requirements["tags"] = None
    fallback_requirements["description"] = None

    fallback_state["requirements"] = fallback_requirements

    products = await search_with_retry(fallback_state)

    print("=== Fallback Debug ===")
    print("Fallback requirements:", fallback_requirements)
    print("Fallback raw products:", len(products))
    print("Fallback filtered products:", len(filtered_products))

    if products is None:
        logger.info("Products search timeout")
        return None

    filtered_products = filter_products(
        products,
        fallback_requirements
    )

    return filtered_products
