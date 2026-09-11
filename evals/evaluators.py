CATEGORY_ALIASES = {
    "无线鼠标": {"无线鼠标", "鼠标"},
    "鼠标": {"无线鼠标", "鼠标"},
}

def get_price_range(predicted):
    price_min = predicted.get("price_min")
    price_max = predicted.get("price_max")

    if price_min is not None or price_max is not None:
        return price_min, price_max

    price_preference = predicted.get("price_preference")

    if price_preference:
        import re

        match = re.search(r"(\d+)", price_preference)

        if match:
            price = float(match.group(1))
            return price * 0.8, price * 1.2

    return None, None

def evaluate_requirements(predicted:dict,expected:dict):

    results = {}

    for field,expected_value in expected.items():

        if field == "tags":
            predicted_tags = predicted.get("tags", [])
            expected_tags = expected_value

            results[field] = all(
                any(
                    expected_tag in predicted_tag
                    for predicted_tag in predicted_tags
                )
                for expected_tag in expected_tags
            )
        elif field in ("price_min","price_max"):
            predicted_min, predicted_max = get_price_range(predicted)

            if predicted_min is None or predicted_max is None:
                results[field] = False
                continue

            expected_min = expected.get("price_min")
            expected_max = expected.get("price_max")

            if expected_min is None:
                results[field] = predicted_min <= expected_max

            elif expected_max is None:
                results[field] = predicted_max >= expected_min

            else:
                results[field] = (
                        predicted_max >= expected_min
                        and predicted_min <= expected_max
                )

        elif field == "category":
            predicted_category = predicted.get("category")

            aliases = CATEGORY_ALIASES.get(
                expected_value,
                {expected_value}
            )

            results[field] = predicted_category in aliases

        else:
            results[field] = (predicted.get(field) == expected_value)

    score = sum(results.values())
    total = len(results)

    return {
        "results": results,
        "score": score,
        "total": total,
        "accuracy": score / total if total else 0
    }
