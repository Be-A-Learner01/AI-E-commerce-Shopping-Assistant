import asyncio

from app.models.llm import requirement_model
from langchain_core.messages import HumanMessage,SystemMessage
from agent.prompts import REQUIREMENT_PROMPTS



async def test_requirement():
    response = await requirement_model.ainvoke([
        SystemMessage(content=REQUIREMENT_PROMPTS),

        HumanMessage(content="""
    以下是当前用户相关的长期记忆：
    用户购买跑鞋的预算约800元，偏好Nike品牌，主要用于日常跑5公里，注重透气性。
    用户想买Nike跑鞋，预算800元左右，主要用于日常跑5公里。
    用户购买跑鞋偏好：偏好Nike品牌，预算约800元以内，主要用于日常5公里跑步。
    """),

        HumanMessage(
            content="预算800块，想买双Nike跑鞋，主要平时跑5公里"
        ),
    ])

    print("TYPE:", type(response))
    print("RESULT:", response)

if __name__ == "__main__":
    asyncio.run(test_requirement())