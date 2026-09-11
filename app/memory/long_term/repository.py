from sqlalchemy.orm import Session
from schemas.memory_schema import Memory
from utils.text_converter import embed_text
from langsmith import traceable
from utils.loggings import logger

@traceable(name="create_memory")
def create_memory(
        db:Session,
        user_id:str,
        content:str,
        memory_type:str,
        importance:float,
):
    embeddings = embed_text(content)
    memory = Memory(
        user_id=user_id,
        content=content,
        memory_type=memory_type,
        importance=importance,
        embeddings=embeddings,
    )
    db.add(memory)
    db.commit()
    db.refresh(memory)
    return memory

@traceable(name="get_memory")
def get_memory(db:Session,memory_id:str):
    return (
        db.query(Memory).filter(Memory.memory_id == memory_id).first()
    )
@traceable(name="get_memories_by_user")
def get_memories_by_user(db:Session,user_id:str):
    return (
        db.query(Memory).filter(Memory.user_id == user_id).all()
    )

@traceable(name="update_memory")
def update_memory(
        db:Session,
        memory_id: str,
        content:str | None = None,
        memory_type:str | None = None,
        importance:float | None = None,
        embeddings:list[float] | None = None
):
    memory = get_memory(db,memory_id=memory_id)

    if memory is None:
        return None

    if content is not None:
        memory.content = content

    if memory_type is not None:
        memory.memory_type = memory_type

    if importance is not  None:
        memory.importance = importance

    if embeddings is not None:
        memory.embeddings = embeddings

    db.commit()
    db.refresh(memory)

    return memory


def delete_memory(db:Session,memory_id:str):
    memory = get_memory(db=db,memory_id=memory_id)

    if memory is None:
        return None
    db.delete(memory)
    db.commit()

    return memory

def delete_memories_by_user(db:Session,user_id:str):
    memory = get_memories_by_user(db=db,user_id=user_id)
    if memory is not None:
        return None
    db.delete(memory)
    db.commit()
    print("删除成功！")
    return memory

@traceable(name="search_memories")
def search_memories(
        db:Session,
        user_id:str,
        query:str,
        top_k:int = 5,
        threshold:float = 0.6
):
    query_embeddings = embed_text(query)
    distance = Memory.embeddings.cosine_distance(query_embeddings)
    try:
        logger.info("Memory search started")
        result = (
            db.query(Memory,
                     distance.label("distance"))
            .filter(Memory.user_id == user_id,
                    distance <= 1 - threshold)
            .order_by(distance)
            .limit(top_k)
            .all()
        )
        logger.info("Memory search completed")
        return result
    except Exception:
        logger.exception("Memory search failed")
        raise

@traceable(name="find_similar_memories")
def find_similar_memories(
        db:Session,
        user_id:str,
        query:str,
        top_k:int = 1
):
    query_embeddings = embed_text(query)
    return (
        db.query(
            Memory,
            Memory.embeddings.cosine_distance(query_embeddings).label("distance")
        )
        .filter(Memory.user_id == user_id)
        .order_by(
            Memory.embeddings.cosine_distance(query_embeddings)
        ).limit(top_k)
        .all()
    )

@traceable(name="is_duplicate")
def is_duplicate(similar_memories,threshold:float = 0.90) -> bool:
    if not similar_memories:
        return False
    _,distance = similar_memories[0]
    similarity = 1 -distance
    return similarity >= threshold


