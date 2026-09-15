from app.memory.long_term.repository import create_memory
from app.memory.long_term.postgres import SessionLocal

db = SessionLocal()
import asyncio

async def main():
    create_memory(
        db=db,
        user_id="eval_memory",
        content="用户偏好三星手机",
        memory_type="preference",
        importance=0.8,
    )

    create_memory(
        db=db,
        user_id="eval_memory",
        content="用户购买手机时比较看重拍照",
        memory_type="preference",
        importance=0.8,
    )

    create_memory(
        db=db,
        user_id="eval_memory",
        content="用户平时经常跑步",
        memory_type="habit",
        importance=0.8,
    )

if __name__ == "__main__":
    asyncio.run(main())