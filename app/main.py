from app.agent.graph import agent
from langchain_core.messages import HumanMessage
import asyncio
query=("我想买一个4000元内的平板电脑")


async def main():
    answer = await agent.ainvoke(
        {"query":query}
    )
    print(answer["answer"])
if __name__ == "__main__":
    asyncio.run(main())

