import re
def get_price_range(predicted):
    price_min = predicted.get("price_min")
    price_max = predicted.get("price_max")

    if price_min is not None or price_max is not None:
        return price_min, price_max

    price_preference = predicted.get("price_preference")

    if price_preference:

        match = re.search(r"(\d+)", price_preference)

        if match:
            price = float(match.group(1))
            return price * 0.9, price * 1.1

    return None, None