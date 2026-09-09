import asyncio
import time

from app.agent.graph import create_agent


async def evaluate_latency():
    agent, conn = await create_agent()

    try:
        config = {
            "configurable": {
                "thread_id": "latency_test_001"
            }
        }

        start = time.perf_counter()

        result = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "我想买一台三星手机，预算8000元以内。"
                    }
                ],
                "query": "我想买一台三星手机，预算8000元以内。",
                "memories": [],
                "requirements": {},
                "products": [],
                "answer": "",
                "error": None,
            },
            config=config,
        )

        elapsed = time.perf_counter() - start

        print("\n====================")
        print("Latency Evaluation")
        print("====================")

        print(f"Total latency: {elapsed:.2f}s")
        print(f"Products: {len(result.get('products', []))}")
        print(f"Answer exists: {bool(result.get('answer'))}")
        print(f"Error: {result.get('error')}")

        if result.get("answer") and result.get("error") is None:
            print("\nResult: PASS")
        else:
            print("\nResult: FAIL")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(evaluate_latency())