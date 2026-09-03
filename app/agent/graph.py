from langgraph.graph import StateGraph,START,END
from .state import AgentState
from .nodes import requirement_node,product_node,answer_node
from langgraph.checkpoint.memory import MemorySaver
import asyncio


checkpointer = MemorySaver()

agent_builder = StateGraph(AgentState)
agent_builder.add_node("requirement_node",requirement_node)
agent_builder.add_node("product_node",product_node)
agent_builder.add_node("answer_node",answer_node)
agent_builder.add_edge(START,"requirement_node")
agent_builder.add_edge("requirement_node","product_node")
agent_builder.add_edge("product_node","answer_node")
agent_builder.add_edge("answer_node",END)
agent  = agent_builder.compile()

