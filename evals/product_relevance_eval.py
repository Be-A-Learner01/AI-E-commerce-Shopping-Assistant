from tools.product_match import match_product
from langchain_core.messages import ToolMessage
import json

def evaluate_product_relevance(tool_message: ToolMessage | None, requirements: dict):
    products = []

    if tool_message:
        content = tool_message.content

        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                content = {}

        if isinstance(content, dict):
            products = content.get("products", [])

    if not products:
        return {
            "score": 0,
            "total": 0,
            "relevant": 0,
            "details": []
        }
    details = []
    relevant = 0

    for product in products:
        matched,reasons = match_product(product,requirements)

        if matched:
            relevant += 1

        details.append({
            "product_id": product.get("id"),
            "relevant": matched,
            "reasons": reasons
        })

    score = relevant / len(products)

    return {
        "score": score,
        "total": len(products),
        "relevant": relevant,
        "details": details
    }