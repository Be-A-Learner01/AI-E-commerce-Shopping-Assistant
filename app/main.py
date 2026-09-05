from app.agent.graph import agent
from dotenv import load_dotenv
import asyncio
from langchain_core.messages import HumanMessage

load_dotenv()

config = {
    "configurable": {
        "thread_id": "user_001"
    }
}


async def main(query):
    answer = await agent.ainvoke(
    {"query": query,
        "messages": [
            HumanMessage(content=query)
        ]
    },
    config=config
    )
    print("本次回答：")
    print(answer["answer"])
    print(agent.get_state(config))
if __name__ == "__main__":
    query1 = "我想买苹果手机，有没有"
    query2 = "有没有256gb?"

    asyncio.run(main(query1))
    asyncio.run(main(query2))


