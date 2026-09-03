from langgraph.graph import StateGraph,START,END
from state import AgentState
from nodes import requirement_node
from langgraph.checkpoint.memory import MemorySaver
import asyncio

checkpointer = MemorySaver()

agent_builder = StateGraph(AgentState)
agent_builder.add_node("requirement_node",requirement_node)
agent_builder.add_edge(START,"requirement_node")
agent_builder.add_edge("requirement_node",END)
agent  = agent_builder.compile(
)
query="我想买一双500元的运动鞋"
async def main():
    answer = await agent.ainvoke(
    {"query":query}
    )
    for a,cont in answer.items():
        print(a,cont)
asyncio.run(main())
