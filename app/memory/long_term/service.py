from app.memory.long_term.repository import (find_similar_memories,is_duplicate,update_memory,create_memory)
from .postgres import SessionLocal
from .conflict import detect_memory_conflict

async def save_memory(
        user_id:str,
        content:str,
        memory_type:str |None,
        importance:float | None
):
    db = SessionLocal()
    try:
        # find similar memory
        similar_memories = find_similar_memories(
            db=db,
            user_id=user_id,
            query=content,
            top_k=1
        )

        #dedup
        if is_duplicate(similar_memories):
            return {"action":"dedup"}

        # conflict
        if similar_memories:
            existing_memory,distance = similar_memories[0]

            conflict = await detect_memory_conflict(existing_memory=existing_memory.content,
                                              new_memory=content)
            if conflict:
                update_memory(
                    db=db,
                    memory_id=existing_memory.memory_id,
                    content=content,
                    memory_type=memory_type,
                    importance=importance
                )

                return {"action":"update"}

        # create memory
        create_memory(
            db=db,
            user_id=user_id,
            content=content,
            memory_type=memory_type,
            importance=importance
        )
        return {"action":"create"}
    finally:
        db.close()