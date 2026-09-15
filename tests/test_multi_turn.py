import asyncio
from langchain_core.messages import HumanMessage
from app.agent.graph import create_agent


async def main():
    agent, conn = await create_agent()

    thread_id = "test-multi-turn-001"

    try:
        # =========================
        # 第一轮
        # =========================
        print("\n========== 第一轮 ==========\n")

        result1 = await agent.ainvoke(
            {
                "user_id": "test001",
                "messages": [
                    HumanMessage(content="我想买一台8000元以内的苹果手机")
                ],
                "memories": [],
            },
            config={
                "configurable": {
                    "thread_id": thread_id
                }
            }
        )

        for message in result1["messages"]:
            print(f"--- {type(message).__name__} ---")
            print("content:", message.content)

            if getattr(message, "tool_calls", None):
                print("tool_calls:", message.tool_calls)

        # =========================
        # 第二轮
        # =========================
        print("\n========== 第二轮 ==========\n")

        result2 = await agent.ainvoke(
            {
                "messages": [
                    HumanMessage(content="那它有几个存储版本？")
                ]
            },
            config={
                "configurable": {
                    "thread_id": thread_id
                }
            }
        )

        for message in result2["messages"]:
            print(f"--- {type(message).__name__} ---")
            print("content:", message.content)

            if getattr(message, "tool_calls", None):
                print("tool_calls:", message.tool_calls)

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())