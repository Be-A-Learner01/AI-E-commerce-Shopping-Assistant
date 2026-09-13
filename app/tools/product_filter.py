BRAND_MAP = {
    "苹果": "Apple",
    "三星": "Samsung",
    "华为": "Huawei",
    "小米": "Xiaomi",
    "索尼": "Sony",
}

def filter_products(products, requirements):

    expected_brand = requirements.get("brand")

    if expected_brand:
            expected_brand = BRAND_MAP.get(
                expected_brand,
                expected_brand
            )

    filtered_products = []

    for item in products:

        product = item["document"].metadata["product"]

        if expected_brand:
            if product["brand"] != expected_brand:
                continue

        expected_category = requirements.get("category")

        if expected_category:
            if product.get("category") !=expected_category:
                continue
        price_max = requirements.get("price_max")
        if price_max:
            if product.get("price",0) > requirements["price_max"]:
                continue

        price_min = requirements.get("price_min")
        if price_min:
            if product.get("price",0)< requirements["price_min"]:
                continue

        expected_colors = requirements.get("color")
        if expected_colors:
            product_color = product.get("color")
            if product_color not in expected_colors:
                continue

        expected_sizes = requirements.get("sizes")
        if expected_sizes:
            product_sizes = product.get("sizes",[])
            if not any(size in product_sizes for size in expected_sizes):
                continue

        expected_storage = requirements.get("storage")
        if expected_storage:
            product_storages = product.get("storage",[])
            if not any(storage in product_storages for storage in expected_storage):
                continue

        filtered_products.append(item)

    return filtered_products
