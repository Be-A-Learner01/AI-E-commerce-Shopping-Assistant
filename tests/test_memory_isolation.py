import asyncio

from langchain_core.messages import HumanMessage

from app.agent.graph import create_agent
from app.memory.long_term.postgres import SessionLocal
from app.memory.long_term.repository import search_memories

#测试长期 memory 的隔离效果

async def main():
    agent, conn = await create_agent()

    user_a = "memory_test_user_A"
    user_b = "memory_test_user_B"

    thread_a = "memory_test_thread_A"
    thread_b = "memory_test_thread_B"

    try:
        print("\n========== 用户 A 写入长期记忆 ==========")

        await agent.ainvoke(
            {
                "user_id": user_a,
                "messages": [
                    HumanMessage(content="我比较喜欢三星手机")
                ],
            },
            config={
                "configurable": {
                    "thread_id": thread_a
                }
            },
        )

        print("\n========== 检查用户 A 的 Memory ==========")

        db = SessionLocal()
        try:
            memories_a = search_memories(
                db=db,
                user_id=user_a,
                query="推荐手机",
                top_k=5,
            )

            for memory, distance in memories_a:
                print(
                    f"user={memory.user_id} | "
                    f"content={memory.content} | "
                    f"distance={distance:.4f}"
                )
        finally:
            db.close()

        print("\n========== 用户 B 查询长期记忆 ==========")

        await agent.ainvoke(
            {
                "user_id": user_b,
                "messages": [
                    HumanMessage(content="那你推荐一台手机给我")
                ],
            },
            config={
                "configurable": {
                    "thread_id": thread_b
                }
            },
        )

        print("\n========== 直接检查用户 B 的 Memory ==========")

        db = SessionLocal()
        try:
            memories_b = search_memories(
                db=db,
                user_id=user_b,
                query="推荐手机",
                top_k=5,
            )

            if not memories_b:
                print("✅ 用户 B 没有检索到用户 A 的长期记忆")
            else:
                for memory, distance in memories_b:
                    print(
                        f"user={memory.user_id} | "
                        f"content={memory.content} | "
                        f"distance={distance:.4f}"
                    )

        finally:
            db.close()

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())