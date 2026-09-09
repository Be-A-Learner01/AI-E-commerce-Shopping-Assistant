import asyncio

from app.agent.nodes import requirement_model
from app.agent.prompts import REQUIREMENT_PROMPTS
from app.retrieval.reranker import rerank_results
from langchain_core.messages import HumanMessage, SystemMessage


CASES = [
    {
        "name": "apple_phone",
        "input": "我想买一台苹果手机。",
        "expected_brand": "Apple",
        "expected_category": "手机",
    },
    {
        "name": "samsung_phone",
        "input": "我想买一台三星手机。",
        "expected_brand": "Samsung",
        "expected_category": "手机",
    },
    {
        "name": "sports_shoes",
        "input": "我想买一双运动鞋。",
        "expected_category": "运动鞋",
    },
]


async def build_state(user_input):
    response = await requirement_model.ainvoke([
        SystemMessage(content=REQUIREMENT_PROMPTS),
        HumanMessage(content=user_input),
    ])

    return {
        "query": user_input,
        "requirements": response.model_dump(),
    }


def match_product(product, case):
    if "expected_brand" in case:
        if product["brand"] != case["expected_brand"]:
            return False

    if "expected_category" in case:
        if product["category"] != case["expected_category"]:
            return False

    return True


async def evaluate_rag():
    correct = 0

    for case in CASES:
        state = await build_state(case["input"])

        results = rerank_results(state)

        print("\n====================")
        print("Case:", case["name"])
        print("Query:", case["input"])

        if not results:
            print("Result: FAIL")
            print("Reason: 没有检索结果")
            continue

        print("\nTop Results:")

        for i, item in enumerate(results, start=1):
            product = item["document"].metadata["product"]
            score = item["rerank_score"]

            print(
                f"{i}. "
                f"{product['brand']} "
                f"{product['name']} "
                f"category={product['category']} "
                f"price={product['price']} "
                f"score={score:.4f}"
            )

        # Top-K Recall：
        # 只要 Top-K 中存在符合条件的商品，就算成功
        passed = False

        for item in results:
            product = item["document"].metadata["product"]

            if match_product(product, case):
                passed = True
                break

        if passed:
            correct += 1
            print("\nResult: PASS")
        else:
            print("\nResult: FAIL")

    accuracy = correct / len(CASES)

    print("\n====================")
    print("RAG Evaluation")
    print(f"Passed: {correct}/{len(CASES)}")
    print(f"Top-K Recall: {accuracy:.2%}")


if __name__ == "__main__":
    asyncio.run(evaluate_rag())