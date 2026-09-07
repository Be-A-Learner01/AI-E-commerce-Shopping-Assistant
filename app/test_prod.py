from memory.long_term.postgres import SessionLocal
from memory.long_term.repository import search_memories
db = SessionLocal()
def test_memory_retrieval(db):
    print("Start")
    memories = search_memories(
        db=db,
        user_id="test001",
        query="我想买三星手机",
        top_k=5,
    )

    print("=== Memory Retrieval ===")

    for memory, distance in memories:
        print(
            f"content: {memory.content}"
        )
        print(
            f"distance: {distance}"
        )
        print("---")

test_memory_retrieval(db)