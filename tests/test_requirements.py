import asyncio

from langchain_core.messages import HumanMessage, SystemMessage

from app.agent.nodes import requirement_model
from app.agent.prompts import REQUIREMENT_PROMPTS


CASES = [
    {
        "name": "brand_and_budget",
        "input": "我想买一台苹果手机，预算5000元以内。",
        "expected": {
            "category": "手机",
            "brand": "苹果",
            "price_max": 5000,
        },
    },
    {
        "name": "complex_requirement",
        "input": "我想买三星手机，预算5000到8000元，1TB，紫色。",
        "expected": {
            "category": "手机",
            "brand": "三星",
            "price_min": 5000,
            "price_max": 8000,
            "storage": "1TB",
            "color": ["紫色"],
        },
    },
    {
        "name": "category_only",
        "input": "我想买一台手机。",
        "expected": {
            "category": "手机",
        },
    },
    {
        "name": "multiple_colors",
        "input": "我想买苹果手机，预算6000元以内，黑色或者白色都可以。",
        "expected": {
            "category": "手机",
            "brand": "苹果",
            "price_max": 6000,
            "color": ["黑色", "白色"],
        },
    },
]


def check_result(actual, expected):
    """
    只检查 expected 中明确要求的字段。
    没有要求的字段不参与评分。
    """
    for key, expected_value in expected.items():
        actual_value = actual.get(key)

        if actual_value != expected_value:
            return False, key, actual_value, expected_value

    return True, None, None, None


async def evaluate_requirement():
    correct = 0

    for case in CASES:

        response = await requirement_model.ainvoke([
            SystemMessage(content=REQUIREMENT_PROMPTS),
            HumanMessage(content=case["input"]),
        ])

        actual = response.model_dump()

        passed, field, actual_value, expected_value = check_result(
            actual,
            case["expected"]
        )

        if passed:
            correct += 1

        print("\n====================")
        print("Case:", case["name"])
        print("Input:", case["input"])
        print("Expected:", case["expected"])
        print("Actual:", actual)

        if passed:
            print("Result: PASS")
        else:
            print("Result: FAIL")
            print("Failed field:", field)
            print("Expected value:", expected_value)
            print("Actual value:", actual_value)

    accuracy = correct / len(CASES)

    print("\n====================")
    print("Requirement Evaluation")
    print(f"Passed: {correct}/{len(CASES)}")
    print(f"Accuracy: {accuracy:.2%}")


if __name__ == "__main__":
    asyncio.run(evaluate_requirement())