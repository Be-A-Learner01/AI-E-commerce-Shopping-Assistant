
BRAND_MAP = {
    "苹果": "Apple",
    "三星": "Samsung",
    "华为": "Huawei",
    "小米": "Xiaomi",
    "索尼": "Sony",
}

def has_matching_product(products, requirements):
    expected_brand = requirements.get("brand")

    if expected_brand:
            expected_brand = BRAND_MAP.get(
                expected_brand,
                expected_brand
            )

    for item in products:
        product = item["document"].metadata["product"]

        if expected_brand:
            if product["brand"] != expected_brand:
                continue

        if requirements.get("price_max") is not None:
            if product["price"] > requirements["price_max"]:
                continue

        if requirements.get("price_min") is not None:
            if product["price"] < requirements["price_min"]:
                continue

        return True

    return False