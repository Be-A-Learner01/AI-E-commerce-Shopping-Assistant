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
if __name__ == "__main__":
    query = "我现在更喜欢三星手机了。"
    asyncio.run(main(query))



