from app.tools.product_search import search_with_fallback
from app.agent.state import AgentState


TEST_CASES = [
    {
        "name": "正常搜索",
        "requirements": {
            "category": "手机",
            "brand": "三星",
            "color": None,
            "sizes": None,
            "storage": None,
            "tags": None,
            "description": None,
            "price_min": None,
            "price_max": None,
            "price_preference": None,
        },
        "expect_products": True,
    },
    {
        "name": "Fallback",
        "requirements": {
            "category": "手机",
            "brand": "三星",
            "color": ["不存在的颜色"],
            "sizes": None,
            "storage": "999TB",
            "tags": ["不存在的标签"],
            "description": "不存在的商品",
            "price_min": None,
            "price_max": None,
            "price_preference": None,
        },
        "expect_products": True,
    },
]


async def evaluate_case(case):
    state = AgentState(
        user_id="eval_fallback",
        messages=[],
        memories=[],
        requirements=case["requirements"],
        products=[],
        answer="",
        error=None,
    )

    products = await search_with_fallback(state)

    passed = (
        bool(products) == case["expect_products"]
    )

    print("\n====================")
    print(f"Case: {case['name']}")
    print(f"Expected products: {case['expect_products']}")
    print(f"Actual products: {bool(products)}")
    print(f"Result: {'PASS' if passed else 'FAIL'}")

    if products:
        print("\nProducts:")
        for product in products:
            print(
                f"- {product.get('name')} "
                f"| {product.get('brand')} "
                f"| {product.get('price')}"
            )

    return passed


async def main():
    passed_count = 0

    for case in TEST_CASES:
        if await evaluate_case(case):
            passed_count += 1

    print("\n====================")
    print("Final Evaluation")
    print("====================")

    print(
        f"Passed: {passed_count}/{len(TEST_CASES)}"
    )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())