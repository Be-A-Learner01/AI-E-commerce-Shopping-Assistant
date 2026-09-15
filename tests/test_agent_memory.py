import asyncio
from langchain_core.messages import HumanMessage
from app.agent.graph import create_agent
from app.memory.long_term.repository import get_memories_by_user,delete_memories_by_user
from app.memory.long_term.postgres import SessionLocal




async def main():
    agent, conn = await create_agent()

    thread_id_1 = "test-memory-agent-001"
    thread_id_2 = "test-memory-agent-002"
    db = SessionLocal()
    user_id = "test001"
    try:
        # =========================
        # 第一轮：写入长期记忆
        # =========================
        print("\n========== 第一轮 ==========\n")

        result1 = await agent.ainvoke(
            {
                "user_id": user_id,
                "messages": [
                    HumanMessage(content="我比较喜欢三星手机")
                ],
                "memories": [],
            },
            config={
                "configurable": {
                    "thread_id": thread_id_1
                }
            },
        )

        for message in result1["messages"]:
            print(f"--- {type(message).__name__} ---")
            print("content:", message.content)

            if getattr(message, "tool_calls", None):
                print("tool_calls:", message.tool_calls)

        # =========================
        # 第二轮：依赖长期记忆推荐
        # =========================
        print("\n========== 第二轮 ==========\n")

        result2 = await agent.ainvoke(
            {
                "messages": [
                    HumanMessage(content="那你推荐一台手机给我")
                ]
            },
            config={
                "configurable": {
                    "thread_id": thread_id_2
                }
            },
        )

        for message in result2["messages"]:
            print(f"--- {type(message).__name__} ---")
            print("content:", message.content)

            if getattr(message, "tool_calls", None):
                print("tool_calls:", message.tool_calls)

        memories = get_memories_by_user(db,user_id)

        print("\n========== USER MEMORIES ==========\n")
        if not memories:
            print("没有找到长期记忆")
            return

        for memory in memories:
            print(f"ID: {memory.id}")
            print(f"Content: {memory.content}")
            print(f"Type: {memory.memory_type}")
            print(f"Importance: {memory.importance}")
            print(f"Created: {memory.created_at}")
            print("-" * 50)
        delete_memories_by_user(db,user_id)
    finally:
        await conn.close()
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
