from app.memory.long_term.postgres import SessionLocal
from app.memory.long_term.repository import create_memory,search_memories,delete_memories_by_user
from app.schemas.memory_schema import Memory


def clear_test_memories(db, user_id: str):
    db.query(Memory).filter(
        Memory.user_id == user_id
    ).delete(synchronize_session=False)

    db.commit()


def test_retrieval():
    user_id = "retrieval_test"

    db = SessionLocal()

    try:

        delete_memories_by_user(db, user_id)

        create_memory(
            db=db,
            user_id=user_id,
            content="用户偏好三星手机",
            memory_type="preference",
            importance=0.8
        )

        create_memory(
            db=db,
            user_id=user_id,
            content="用户购买手机时比较看重拍照",
            memory_type="preference",
            importance=0.8
        )

        create_memory(
            db=db,
            user_id=user_id,
            content="用户平时经常跑步",
            memory_type="habit",
            importance=0.7
        )

        queries = [
            ("三星手机", True),
            ("手机推荐", True),
            ("跑鞋", True),
        ]

        for query, expected in queries:

            results = search_memories(
                db=db,
                user_id=user_id,
                query=query,
                top_k=5,
                threshold=0.4
            )

            found = len(results) > 0

            print(f"\nQuery: {query}")
            print(f"Expected: {expected}")
            print(f"Actual  : {found}")

            for memory, distance in results:
                similarity = 1 - distance

                print(
                    f"  {memory.content} "
                    f"| similarity={similarity:.4f}"
                )

            assert found == expected

            print("✅ PASS")

    finally:
        db.close()


if __name__ == "__main__":
    test_retrieval()