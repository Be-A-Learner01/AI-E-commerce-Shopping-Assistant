from sqlalchemy.orm import Session
from schemas.memory_schema import Memory
from utils.text_converter import embed_text

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

def get_memories_list(db:Session,user_id:str):
    return (
        db.query(Memory).filter(Memory.user_id == user_id).all()
    )

def get_memory(db:Session,memory_id:str):
    return (
        db.query(Memory).filter(Memory.memory_id == memory_id).first()
    )

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
        memory.importance = importance,

    if embeddings is not None:
        memory.embeddings = embeddings

    db.commit()
    db.refresh(memory)

    return memory

def delete_memory(db:Session,memory_id:str):
    memory = get_memory(db=db,memory_id=memory_id)

    if memory is not None:
        return None
    db.delete(memory)
    db.commit()

    return memory

def delete_memories_by_user(db:Session,user_id:str):
    memory = get_memories_list(db=db,user_id=user_id)
    if memory is not None:
        return None
    db.delete(memory)
    db.commit()

    return memory

def search_memories(
        db:Session,
        user_id:str,
        query:str,
        top_k:int = 5,
):
    query_embeddings = embed_text(query)
    return (
        db.query(Memory).filter(Memory.user_id == user_id)
        .order_by(Memory.embeddings.cosine_distance(query_embeddings))
        .limit(top_k)
        .all()
    )
