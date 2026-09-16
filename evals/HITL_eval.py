import asyncio
import uuid

from langchain_core.messages import HumanMessage
from langgraph.types import Command

from app.agent.graph import create_agent


TEST_CASES = [
    {
        "id": "hitl_001",
        "query": "帮我推荐一台5000元左右的手机",
        "should_interrupt": True,
    },
    {
        "id": "hitl_002",
        "query": "帮我推荐一款适合日常跑步的跑鞋",
        "should_interrupt": True,
    },
    {
        "id": "hitl_003",
        "query": "你好",
        "should_interrupt": False,
    },
]


async def run_case(case):
    agent, conn = await create_agent()

    thread_id = str(uuid.uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    try:
        # 第一次执行
        result = await agent.ainvoke(
            {
                "user_id": "test001",
                "messages": [
                    HumanMessage(content=case["query"])
                ],
            },
            config=config,
        )

        interrupts = result.get("__interrupt__")

        actual_interrupt = bool(interrupts)

        print(f"\n=== {case['id']} ===")
        print(f"query: {case['query']}")
        print(f"should_interrupt: {case['should_interrupt']}")
        print(f"actual_interrupt: {actual_interrupt}")

        # HITL Case
        if actual_interrupt:

            # 模拟用户选择第一个商品
            result = await agent.ainvoke(
                Command(resume="1"),
                config=config,
            )

            completed = not result.get("__interrupt__")

            print(f"resume: 1")
            print(f"completed: {completed}")

            return (
                actual_interrupt == case["should_interrupt"]
                and completed
            )

        # 非 HITL Case
        return actual_interrupt == case["should_interrupt"]

    finally:
        await conn.close()


async def main():
    passed = 0

    for case in TEST_CASES:
        success = await run_case(case)

        if success:
            passed += 1
            print("PASS")
        else:
            print("FAIL")

    print("\n====================")
    print(f"HITL Evaluation: {passed}/{len(TEST_CASES)}")
    print("====================")


if __name__ == "__main__":
    asyncio.run(main())