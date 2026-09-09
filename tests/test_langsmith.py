import asyncio

from app.agent.graph import create_agent


async def evaluate_langsmith():
    agent, conn = await create_agent()

    try:
        config = {
            "configurable": {
                "thread_id": "eval_langsmith_001"
            }
        }

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

        print("\n====================")
        print("LangSmith Evaluation")
        print("====================")

        print("Answer:")
        print(result.get("answer"))

        print("\nProducts:")
        print(len(result.get("products", [])))

        print("\nRequirements:")
        print(result.get("requirements"))

        print("\nError:")
        print(result.get("error"))

        if result.get("answer"):
            print("\nResult: PASS")
        else:
            print("\nResult: FAIL")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(evaluate_langsmith())