from tools.product_match import match_product
def evaluate_product_relevance(products: list[dict], requirements: dict):
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