

from app.agent.graph import create_agent
from dotenv import load_dotenv
import asyncio
from langchain_core.messages import HumanMessage

load_dotenv()




async def main():
    agent,conn = await create_agent()

    config = {
        "configurable": {
            "thread_id": "user_001"
        }
    }
    # 第一轮
    result1 = await agent.ainvoke(
        {
            "query": "我想买一台5000元以内的苹果手机，要求1TB、紫色、折叠屏",
            "messages": [
                HumanMessage(content="我想买一台5000元以内的苹果手机，要求1TB、紫色、折叠屏")
            ],
        },
        config=config
    )

    print("\n===== 第一轮 =====")
    print(result1["answer"])


    await conn.close()
if __name__ == "__main__":
    asyncio.run(main())



