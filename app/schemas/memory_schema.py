from sqlalchemy import Column,Integer,String,Text,DateTime,Float
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector
from datetime import datetime,UTC
import uuid
from pydantic import BaseModel
from typing import Optional,Literal


Base = declarative_base()

class Memory(Base):
    __tablename__ = "memory"

    id = Column(Integer,primary_key=True,index=True)
    memory_id = Column(
        String,
        unique=True,
        index=True,
        nullable=False,
        default=lambda: str(uuid.uuid4())
    )
    user_id = Column(String,index=True,nullable=False)
    content = Column(Text,nullable=False)
    memory_type = Column(String,nullable=False)
    importance = Column(Float,default=0.5)
    embeddings =Column(Vector(1024))
    created_at = Column(DateTime,default= lambda :datetime.now(UTC))
    updated_at = Column(DateTime,default= lambda :datetime.now(UTC),onupdate= lambda :datetime.now(UTC))

class MemoryExtraction(BaseModel):
    memory_save:bool
    user_id:str
    content:Optional[str] = None
    memory_type:Optional[str] = None
    importance:Optional[float] = None

class MemoryConflict(BaseModel):
    conflict:Literal["yes","no"]