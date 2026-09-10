import asyncio
from app.memory.long_term.postgres import SessionLocal
from app.memory.long_term.repository import search_memories


async def test_memory_retrieval():

    db = SessionLocal()

    try:
        user_id = "test001"
        query = "给我推荐一台手机"

        memories = search_memories(
            db=db,
            user_id=user_id,
            query=query,
            top_k=5
        )

        print("\n====================")
        print("Memory Retrieval Test")
        print("====================")

        print("Query:", query)
        print("User:", user_id)

        if not memories:
            print("❌ 没有检索到记忆")
            return

        for i, (memory, distance) in enumerate(memories, start=1):

            similarity = 1 - distance

            print(
                f"{i}. "
                f"content={memory.content}"
            )

            print(
                f"   memory_id={memory.memory_id}"
            )

            print(
                f"   distance={distance:.4f}"
            )

            print(
                f"   similarity={similarity:.4f}"
            )

        print("\n✅ Memory Retrieval Test PASSED")

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_memory_retrieval())