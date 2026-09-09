import asyncio

from app.agent.nodes import requirement_node, product_node
from app.agent.state import AgentState
from langchain_core.messages import HumanMessage


CASES = [
    {
        "name": "normal_match",
        "input": "我想买一台三星手机，预算8000元以内。",
        "expect_error": False,
    },
    {
        "name": "fallback_trigger",
        "input": "我想买一台三星手机，预算5000元以内，紫色，1TB。",
        "expect_error": False,
        "expect_fallback": True,
    },
]


async def evaluate_fallback():
    correct = 0

    for case in CASES:
        print("\n====================")
        print("Case:", case["name"])
        print("Input:", case["input"])

        state = {
            "messages": [
                HumanMessage(content=case["input"])
            ],
            "query": case["input"],
            "memories": [],
            "requirements": {},
            "products": [],
            "answer": "",
            "error": None,
        }

        # 1. Requirement Extraction
        requirement_result = await requirement_node(state)
        state.update(requirement_result)

        # 2. Product Search + Fallback
        product_result = await product_node(state)
        state.update(product_result)

        print("Requirements:", state["requirements"])
        print("Products:", len(state["products"]))
        print("Error:", state["error"])

        passed = True

        # 搜索服务不能报错
        if case["expect_error"] is False:
            if state["error"] is not None:
                passed = False

        # 最终应该有商品
        if len(state["products"]) == 0:
            passed = False

        if passed:
            correct += 1
            print("Result: PASS")
        else:
            print("Result: FAIL")

    accuracy = correct / len(CASES)

    print("\n====================")
    print("Fallback Evaluation")
    print(f"Passed: {correct}/{len(CASES)}")
    print(f"Accuracy: {accuracy:.2%}")


if __name__ == "__main__":
    asyncio.run(evaluate_fallback())