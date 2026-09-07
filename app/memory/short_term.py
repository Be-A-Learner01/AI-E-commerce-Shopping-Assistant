from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

import aiosqlite


conn = aiosqlite.connect(
    "data/checkpoints.db",
    check_same_thread=False
)
async def create_checkpointer():
    return await AsyncSqliteSaver()
checkpointer = create_checkpointer(conn)