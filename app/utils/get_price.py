import re

APPROX_WORDS = ("约", "左右", "大约", "大概", "差不多", "上下")

def get_price_range(predicted):
    price_min = predicted.get("price_min")
    price_max = predicted.get("price_max")
    price_preference = predicted.get("price_preference")

    if price_preference:
        match = re.search(r"(\d+(?:\.\d+)?)", price_preference)

        if match and any(word in price_preference for word in APPROX_WORDS):
            price = float(match.group(1))

            return price * 0.8, price * 1.2

    if price_min is not None or price_max is not None:
        return price_min, price_max

    return None, None