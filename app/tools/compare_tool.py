from langchain_core.tools import tool
from app.tools.get_detail import get_product_by_id

@tool
async def compare_products(product_ids: list[int]):
    """
    根据商品 ID 比较多个商品。
    """
    if len(product_ids) < 2 :
        return {
            "success":False,
            "message":"至少需要两件商品才能进行比较。"
        }
    products = []

    for product_id in product_ids:
        product = get_product_by_id(product_id)

        if product is None:
            return {
                "success": False,
                "message": f"未找到商品 ID: {product_id}"
            }

        products.append(product)

    return {
        "success": True,
        "products": products
    }

