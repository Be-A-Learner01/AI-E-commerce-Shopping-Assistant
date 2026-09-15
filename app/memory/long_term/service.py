from app.memory.long_term.repository import (find_similar_memories,detect_memory_dedup,update_memory,create_memory)
from app.memory.long_term.postgres import SessionLocal
from app.memory.long_term.conflict import detect_memory_conflict
from app.utils.loggings import logger

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
            top_k=5
        )

        if not similar_memories:
            create_memory(
                db=db,
                user_id=user_id,
                content=content,
                memory_type=memory_type,
                importance=importance
            )

            return {"action": "create"}

        existing_memory, distance = similar_memories[0]

        similarity = 1 - distance

        logger.info(
            "Memory similarity: %.4f",
            similarity
        )

        if similarity >= 0.70:

            logger.info(
                "Memory passed semantic similarity threshold"
            )

            duplicate = await detect_memory_dedup(
                existing_memory=existing_memory.content,
                new_memory=content
            )

            logger.info(
                "Memory semantic dedup result: %s",
                duplicate
            )

            if duplicate:
                logger.info(
                    "Memory dedup: duplicate detected"
                )

                return {"action": "dedup"}

        conflict = await detect_memory_conflict(
            existing_memory=existing_memory.content,
            new_memory=content
        )

        logger.info(
            "Memory conflict result: %s",
            conflict
        )

        if conflict:
            update_memory(
                db=db,
                memory_id=existing_memory.memory_id,
                content=content,
                memory_type=memory_type,
                importance=importance
            )

            logger.info(
                "Memory conflict detected, memory updated"
            )

            return {"action": "update"}

        create_memory(
            db=db,
            user_id=user_id,
            content=content,
            memory_type=memory_type,
            importance=importance
        )

        logger.info(
            "Memory created"
        )
        return {"action":"create"}
    finally:
        db.close()