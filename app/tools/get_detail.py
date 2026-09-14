import json
from pathlib import Path
from langchain_core.tools import tool

PRODUCT_FILE =Path(__file__).resolve().parents[1] / "data"

def load_products() -> list[dict]:
    with open(PRODUCT_FILE / "products.json", "r", encoding="utf-8") as p:
        products = json.load(p)
        return products

def get_product_by_id(product_id: int) -> dict | None:
    products = load_products()

    for product in products:
        if product["id"] == product_id:
            return product

    return None

@tool
async def get_product_detail(product_id: int):
    """
    根据商品 ID 查询商品详细信息。

    当用户想了解某个具体商品的详细信息时使用。
    例如：
    - 查询商品 1 的详细信息
    - 介绍一下商品 6
    - 我想了解 Apple iPhone 16 Pro
    """
    product = get_product_by_id(product_id)
    if product is None:
        return {
            "success":False,
            "message":f"未找到商品ID: {product_id}"
        }
    return {
        "success":True,
        "product":product
    }