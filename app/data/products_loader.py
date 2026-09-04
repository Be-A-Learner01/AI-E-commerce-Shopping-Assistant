from pathlib import Path
from langsmith import traceable
from langchain_core.documents import Document
from app.utils.text_converter import dict_to_text
import json

ROOT = Path(__file__).resolve().parents[0]

with open(ROOT / "products.json","r",encoding="utf-8") as p:
    products = json.load(p)

@traceable(name="load_products")
def load_products_docs(products):
    docs:list[Document] = []
    for product in products:
        docs.append(
            Document(
                page_content=dict_to_text(product),
                metadata={
                    "id":product.get("id"),
                    "price": product.get("price"),
                    "name": product.get("name"),
                    "brand": product.get("brand"),
                    "category": product.get("category"),
                }
            )
        )
    return docs