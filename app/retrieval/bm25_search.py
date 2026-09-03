import json
from rank_bm25 import BM25Okapi
with open(r"G:\code\E-commerce-asist\app\data\products.json","r",encoding="utf-8") as j:
    products = json.load(j)
from ..agent.state import AgentState
import jieba

def dict_to_texts(state:AgentState | None = None ,lists:dict|None =None) -> str:
    if state is not None:
        lists = state.get("requirements")
    elif lists is None:
        raise ValueError("state和lists至少传一个")
    parts = []

    category = lists.get("category") or ""
    description = lists.get("description") or ""
    brand = lists.get("brand") or ""

    parts.extend([category] * 2)
    parts.extend([description] * 2)

    if lists.get("brand"):
        parts.append(lists.get("brand"))

    if lists.get("price_max") and lists.get("price_min"):
        parts.append(f'{lists["price_min"]}到{lists["price_max"]}元')
    elif lists.get("price_max"):
        parts.append(f'价格在{lists["price_max"]}元以下')
    elif lists.get("price_min"):
        parts.append(f'价格在{lists["price_min"]}元以上')
    elif lists.get("price"):
        parts.append(f'价格为{lists["price"]}')
    text = " ".join(parts)
    return text

def tokenize(state: AgentState | None = None,lists: dict | None = None):
    text=  dict_to_texts(state,lists)
    tokenized_text = list(jieba.cut(text))
    return tokenized_text

tokenized_products = [
    tokenize(lists=product)
    for product in products
]
bm25 = BM25Okapi(tokenized_products)

def bm25_search(state):
    tokenized_req = tokenize(state)
    scores = bm25.get_scores(tokenized_req)
    top_k = 5
    indices = scores.argsort()[::-1][:top_k]
    results = []
    for index in indices:
        results.append({
            "product": products[index],
            "scores": float(scores[index])
        })
    return results
