from langgraph.graph import StateGraph,START,END
from langgraph.prebuilt import ToolNode
from app.tools import TOOLS
from app.agent.state import AgentState
from app.agent.nodes import (
    requirement_node,
    agent_node,
    memory_retrieval_node,
    memory_write_node,
    human_confirm_node
                             )
import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_core.messages import ToolMessage

tool_node = ToolNode(TOOLS)

def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]

    if last_message.tool_calls:
        return "tool_node"

    for message in messages:
        if (
                isinstance(message,ToolMessage)
                and message.name
        ):
                return "human_confirm_node"

    return "memory_write_node"


agent_builder = StateGraph(AgentState)

agent_builder.add_node("memory_retrieval_node",memory_retrieval_node)
agent_builder.add_node("requirement_node",requirement_node)
agent_builder.add_node("agent_node",agent_node)
agent_builder.add_node("tool_node",tool_node)
agent_builder.add_node("human_confirm_node",human_confirm_node)
agent_builder.add_node("memory_write_node",memory_write_node)

agent_builder.add_edge(START,"memory_retrieval_node")
agent_builder.add_edge("memory_retrieval_node","requirement_node")
agent_builder.add_edge("requirement_node","agent_node")
agent_builder.add_conditional_edges("agent_node",
                                    should_continue,
                                    {
                                        "tool_node":"tool_node",
                                        "human_confirm_node":"human_confirm_node",
                                        "memory_write_node":"memory_write_node"
                                    })
agent_builder.add_edge("tool_node","agent_node")
agent_builder.add_edge("human_confirm_node","memory_write_node")
agent_builder.add_edge("memory_write_node",END)

async def create_agent():
    conn = await aiosqlite.connect("data/checkpoints.db")

    checkpointer = AsyncSqliteSaver(conn)

    agent = agent_builder.compile(
        checkpointer=checkpointer
    )
    return agent,conn
