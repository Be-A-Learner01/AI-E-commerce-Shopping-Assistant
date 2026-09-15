from app.memory.long_term.repository import delete_memories_by_user
from app.memory.long_term.postgres import SessionLocal
db = SessionLocal()
user_id = "test001"

delete_memories_by_user(db,user_id)