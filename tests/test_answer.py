import asyncio

from langchain_core.messages import HumanMessage, SystemMessage

from app.agent.nodes import answer_node
from app.agent.prompts import ANSWER_PROMPTS


CASES = [
    {
        "name": "normal_answer",
        "query": "我想买一台三星手机，预算8000元以内。",
        "requirements": {
            "category": "手机",
            "brand": "三星",
            "price_max": 8000,
        },
        "products": [
            {
                "document": {
                    "page_content": "Samsung Galaxy S25",
                    "metadata": {
                        "product": {
                            "name": "Samsung Galaxy S25",
                            "brand": "Samsung",
                            "category": "手机",
                            "price": 6999,
                            "color": "黑色",
                        }
                    },
                },
                "rerank_score": 0.38,
            }
        ],
        "expected_keywords": ["Galaxy S25"],
    },
    {
        "name": "multiple_products",
        "query": "我想买一台手机，预算5000元以内。",
        "requirements": {
            "category": "手机",
            "price_max": 5000,
        },
        "products": [
            {
                "document": {
                    "page_content": "Xiaomi 15",
                    "metadata": {
                        "product": {
                            "name": "Xiaomi 15",
                            "brand": "Xiaomi",
                            "category": "手机",
                            "price": 4499,
                            "color": "黑色",
                        }
                    },
                },
                "rerank_score": 0.21,
            }
        ],
        "expected_keywords": ["Xiaomi 15"],
    },
    {
        "name": "search_error",
        "query": "我想买一台三星手机。",
        "requirements": {
            "category": "手机",
            "brand": "三星",
        },
        "products": [],
        "error": "商品搜索服务暂时不可用，请稍后再试。",
        "expected_keywords": ["商品搜索服务暂时不可用"],
    },
]


async def evaluate_answer():
    correct = 0

    for case in CASES:
        print("\n====================")
        print("Case:", case["name"])
        print("Query:", case["query"])

        state = {
            "messages": [
                HumanMessage(content=case["query"])
            ],
            "query": case["query"],
            "memories": [],
            "requirements": case["requirements"],
            "products": case["products"],
            "answer": "",
            "error": case.get("error"),
        }

        result = await answer_node(state)

        answer = result["answer"]

        print("\nAnswer:")
        print(answer)

        passed = all(
            keyword in answer
            for keyword in case["expected_keywords"]
        )

        if passed:
            correct += 1
            print("\nResult: PASS")
        else:
            print("\nResult: FAIL")
            print("Expected keywords:", case["expected_keywords"])

    accuracy = correct / len(CASES)

    print("\n====================")
    print("Answer Evaluation")
    print(f"Passed: {correct}/{len(CASES)}")
    print(f"Accuracy: {accuracy:.2%}")


if __name__ == "__main__":
    asyncio.run(evaluate_answer())