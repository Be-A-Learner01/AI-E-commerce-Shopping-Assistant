import asyncio
from langchain_core.messages import HumanMessage
from app.agent.graph import create_agent

#测试 checkpoint 的隔离效果

async def main():
    agent, conn = await create_agent()

    user_id = "checkpoint_test_user"

    thread_a = "checkpoint_test_thread_A"
    thread_b = "checkpoint_test_thread_B"

    try:
        print("\n========== Thread A：写入短期记忆 ==========")

        await agent.ainvoke(
            {
                "user_id": user_id,
                "messages": [
                    HumanMessage(content="我叫张三")
                ],
            },
            config={
                "configurable": {
                    "thread_id": thread_a
                }
            },
        )

        print("\n========== Thread A：继续对话 ==========")

        result_a = await agent.ainvoke(
            {
                "user_id": user_id,
                "messages": [
                    HumanMessage(content="我叫什么？")
                ],
            },
            config={
                "configurable": {
                    "thread_id": thread_a
                }
            },
        )

        print("\nThread A 最终消息：")

        for message in result_a["messages"]:
            print(
                f"--- {type(message).__name__} ---"
            )
            print(message.content)

        print("\n========== Thread B：新会话 ==========")

        result_b = await agent.ainvoke(
            {
                "user_id": user_id,
                "messages": [
                    HumanMessage(content="我叫什么？")
                ],
            },
            config={
                "configurable": {
                    "thread_id": thread_b
                }
            },
        )

        print("\nThread B 最终消息：")

        for message in result_b["messages"]:
            print(
                f"--- {type(message).__name__} ---"
            )
            print(message.content)

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())