from langchain_core.tools import tool
from app.tools.product_search import search_with_fallback

@tool
async def search_products(category: str,
    brand: str | None = None,
    description: str | None = None,
    price_max: float | None = None,
    price_min: float | None = None,
    price_preference: str | None = None,
    sizes: str | None = None,
    storage: str | None = None,
    color: list[str] | None = None,
    tags: list[str] | None = None,):
    """
    根据用户的结构化购物需求搜索商品。

    category: 商品类别，例如 手机、跑鞋、耳机
    brand: 品牌
    description: 商品描述或使用需求
    price_max: 最高价格
    price_min: 最低价格
    price_preference: 价格偏好，例如 5000左右
    sizes: 尺寸，例如 42码
    storage: 存储容量，例如 256GB
    color: 颜色
    tags: 商品标签
    """
    
    requirements = {
        "category": category,
        "brand": brand,
        "description": description,
        "price_max": price_max,
        "price_min": price_min,
        "price_preference": price_preference,
        "sizes": sizes,
        "storage": storage,
        "color": color,
        "tags": tags,
    }

    search_state = {"requirements": requirements}

    products = await search_with_fallback(search_state)

    if products is None:
        return {
            "success": False,
            "message": "商品搜索失败"
        }

    result = []

    for item in products:
        product = item["document"].metadata["product"]

        result.append(
            {
                "id": product["id"],
                "name": product["name"],
                "brand": product.get("brand"),
                "category": product.get("category"),
                "price": product.get("price"),
                "color": product.get("color"),
                "sizes": product.get("sizes"),
                "storage": product.get("storage"),
                "tags": product.get("tags"),
            }
        )
    return {
        "success": True,
        "products": result
    }



