from app.utils.get_price import get_price_range
BRAND_MAP = {
    "苹果": "Apple",
    "三星": "Samsung",
    "华为": "Huawei",
    "小米": "Xiaomi",
    "索尼": "Sony",
}

CATEGORY_MAP = {
    "跑鞋": "运动鞋",
    "运动鞋": "运动鞋",
    "平板电脑": "平板",
    "平板": "平板",
    "机械键盘": "键盘",
    "键盘": "键盘",
    "无线鼠标": "鼠标",
    "鼠标": "鼠标",
    "笔记本":"笔记本电脑",
    "笔记本电脑":"笔记本电脑"
}

def match_product(product,requirements)-> tuple[bool,list[str]]:
    reasons = []

    #Brand match
    expected_brand = requirements.get("brand")

    if expected_brand:
        expected_brand = BRAND_MAP.get(
            expected_brand,
            expected_brand
        )

        if product.get("brand") != expected_brand:
            reasons.append("brand mismatch")
    #Category match
    expected_category = requirements.get("category")

    if expected_category:
        expected_category = CATEGORY_MAP.get(
            expected_category,
            expected_category
        )

        if product.get("category") != expected_category:
            reasons.append("category mismatch")
    #Price match
    price_min,price_max = get_price_range(requirements)

    price = product.get("price", 0)

    if price_max is not None and price > price_max:
        reasons.append("price too high")

    if price_min is not None and price < price_min:
        reasons.append("price too low")
    #Color match
    expected_colors = requirements.get("color") or []

    if expected_colors:
        product_color = product.get("color")

        if product_color not in expected_colors:
            reasons.append("color mismatch")
    #Size match
    expected_sizes = requirements.get("sizes")

    if expected_sizes:
        if isinstance(expected_sizes, str):
            expected_sizes = [expected_sizes]

        product_sizes = product.get("sizes") or []

        if not any(
                size in product_sizes
                for size in expected_sizes
        ):
            reasons.append("size mismatch")
    #Storage match
    expected_storage = requirements.get("storage")

    if expected_storage:
        if isinstance(expected_storage, str):
            expected_storage = [expected_storage]

        product_storage = product.get("storage") or []

        if not any(
                storage in product_storage
                for storage in expected_storage
        ):
            reasons.append("storage mismatch")
    #Tags match
    expected_tags = requirements.get("tags")

    if expected_tags:
        product_tags = product.get("tags") or []
        match_tags = sum(
            any(
                expected_tag in product_tag
                or product_tag in expected_tag
                for product_tag in product_tags
            )
            for expected_tag in expected_tags
        )

        required_matches = min(1,len(expected_tags))

        if match_tags < required_matches:
            reasons.append("tags mismatch")

    return len(reasons) == 0, reasons