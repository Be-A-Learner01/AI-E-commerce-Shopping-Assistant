from app.agent.graph import agent
from dotenv import load_dotenv
import asyncio

load_dotenv()

query = "我想买一双500元左右的运动鞋，平时跑步穿，要透气一点"

async def main():
    answer = await agent.ainvoke(
        {"query":query}
    )
    print(answer["answer"])
if __name__ == "__main__":
    asyncio.run(main())

