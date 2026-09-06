from langgraph.graph import StateGraph,START,END
from .state import AgentState
from .nodes import requirement_node,product_node,answer_node,memory_retrieval_node,memory_write_node
import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

# conn = aiosqlite.connect(
#     "data/checkpoints.db",
#     check_same_thread=False
# )
# async def create_checkpointer():
#     return await AsyncSqliteSaver()
# checkpointer = create_checkpointer(conn)

agent_builder = StateGraph(AgentState)
agent_builder.add_node("memory_retrieval_node",memory_retrieval_node)
agent_builder.add_node("requirement_node",requirement_node)
agent_builder.add_node("product_node",product_node)
agent_builder.add_node("answer_node",answer_node)
agent_builder.add_node("memory_write_node",memory_write_node)
agent_builder.add_edge(START,"memory_retrieval_node")
agent_builder.add_edge("memory_retrieval_node","requirement_node")
agent_builder.add_edge("requirement_node","product_node")
agent_builder.add_edge("product_node","answer_node")
agent_builder.add_edge("answer_node","memory_write_node")
agent_builder.add_edge("memory_write_node",END)

agent  = agent_builder.compile(

)

