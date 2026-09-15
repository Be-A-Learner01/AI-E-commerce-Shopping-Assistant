import asyncio
from langchain_core.messages import HumanMessage
from app.agent.graph import create_agent


async def main():
    agent, conn = await create_agent()

    try:
        result = await agent.ainvoke(
            {
                "user_id": "test001",
                "messages": [
                    HumanMessage(content="比较一下商品6和商品7")
                ],
                "memories": [],
            },
            config={
                "configurable": {
                    "thread_id": "test-compare-001"
                }
            }
        )

        print("\n========== FINAL MESSAGES ==========\n")

        for message in result["messages"]:
            print(f"--- {type(message).__name__} ---")
            print("content:", message.content)

            if getattr(message, "tool_calls", None):
                print("tool_calls:", message.tool_calls)

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())