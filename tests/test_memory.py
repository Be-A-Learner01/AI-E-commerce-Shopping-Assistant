from langchain_core.messages import HumanMessage,SystemMessage
from app.agent.nodes import memory_model
from app.agent.prompts import MEMORY_WRITE_PROMPTS
import asyncio

CASES = [
    {
        "name": "preference",
        "input": "我喜欢三星手机。",
        "expected_save": True,
    },
    {
        "name": "temporary_task",
        "input": "帮我搜索一下5000元以内的手机。",
        "expected_save": False,
    },
    {
        "name": "dedup",
        "input": "我比较喜欢三星品牌的手机。",
        "expected_save": False,
    },
    {
        "name": "conflict",
        "input": "我现在更喜欢苹果手机。",
        "expected_save": True,
    },
    {
        "name": "non_conflict",
        "input": "我也喜欢苹果手机。",
        "expected_save": True,
    },
]
async def evaluate_memory_extraction():

    correct = 0

    for case in CASES:

        response = await memory_model.ainvoke([
            SystemMessage(content=MEMORY_WRITE_PROMPTS),
            HumanMessage(content=case["input"]),
        ])

        actual = response.memory_save
        expected = case["expected_save"]

        passed = actual == expected

        if passed:
            correct += 1

        print("\n====================")
        print("Case:", case["name"])
        print("Input:", case["input"])
        print("Expected:", expected)
        print("Actual:", actual)
        print("Content:", response.content)
        print("Result:", "PASS" if passed else "FAIL")

    accuracy = correct / len(CASES)

    print("\n====================")
    print("Memory Extraction Evaluation")
    print(f"Accuracy: {accuracy:.2%}")

if __name__ == "__main__":
    asyncio.run(evaluate_memory_extraction())