
def outcome_grader(state,reference_outputs):
    products = state["products"]

    max_price = reference_outputs.get("price_max")
    min_price = reference_outputs.get("price_min")

    if max_price is not None and min_price is not None:
        price_pass = all(
            min_price <= product["price"] <= max_price
            for product in products
        )
    elif max_price is not None and min_price is  None:
        price_pass = all(
            product["price"] <= max_price
            for product in products
        )
    elif max_price is  None and min_price is not None:
        price_pass = all(
            min_price <= product["price"]
            for product in products
        )
    else:
        price_pass =True


    category = reference_outputs.get("category")
    if category is not None:
        category_pass = all(
            product["category"] == category
            for product in products
        )
    else:
        category_pass = True

    overpass = price_pass and category_pass

    return {
        "price_pass":price_pass,
        "category_pass":category_pass,
        "overpass":overpass
    }

def evaluator(state,reference_outputs):
    passed = outcome_grader(state,reference_outputs)

    return {
        "key":"outcome",
        "score": 1 if passed["overpass"] else 0
    }