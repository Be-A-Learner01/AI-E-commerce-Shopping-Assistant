from sqlalchemy import Column,Integer,String,Text,DateTime,Float
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import declarative_base
from datetime import datetime,UTC
import uuid


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