import json
from langsmith import traceable
import jieba
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi
from ..agent.state import AgentState
from app.utils.text_converter import dict_to_text
from pathlib import Path
import time

BASE_DIR = Path(__file__).resolve().parents[1]
PRODUCTS_PATH = BASE_DIR/"data"/"products.json"

with open(PRODUCTS_PATH,"r",encoding="utf-8") as j:
    products = json.load(j)

def tokenize(products):
    corpus = []
    for product in products:
        text = dict_to_text(product,exclude_keys=["id","key"])
        tokenized_text = list(jieba.cut(text))
        corpus.append(tokenized_text)
    return corpus

corpus = tokenize(products)
bm25 = BM25Okapi(corpus)

@traceable(name="bm25_search")
def bm25_search(state:AgentState,top_k:int = 20):
    start = time.perf_counter()

    requirements = dict_to_text(state["requirements"])
    tokenized_req = list(jieba.cut(requirements))
    scores = bm25.get_scores(tokenized_req)
    indices = scores.argsort()[::-1][:top_k]
    results = []
    for index in indices:
        product = products[index]
        doc = Document(
            page_content = dict_to_text(product),
            metadata = {
                "id":product["id"],
                "product":product,
                "bm25_score":float(scores[index])
            }
        )
        results.append(doc)
    elapsed = time.perf_counter() - start
    print(f"=== Latency === bm25_search: {elapsed:.2f}s")
    return results


