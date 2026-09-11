from app.agent.graph import create_agent
from dotenv import load_dotenv
import asyncio
from langchain_core.messages import HumanMessage
from utils.loggings import setup_logging
load_dotenv()
setup_logging()


async def main():
    agent,conn = await create_agent()

    config = {
        "configurable": {
            "thread_id": "user_001"
        }
    }


    result = await agent.ainvoke(
        {
            "query": "我想买一台4000元以内的三星手机",
            "messages": [
                HumanMessage(content="我想买一台4000元以内的三星手机")
            ],
        },
        config=config
    )

    await conn.close()

    return {"answer":result}

if __name__ == "__main__":

    asyncio.run(main())



