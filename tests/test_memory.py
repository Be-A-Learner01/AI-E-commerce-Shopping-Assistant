import asyncio

from langchain_core.messages import HumanMessage

from app.agent.nodes import memory_write_node
from app.memory.long_term.postgres import SessionLocal
from app.schemas.memory_schema import Memory

TEST_CASES = [
    # =========================
    # ① 当前一次性需求
    # =========================
    {
        "id": "001",
        "query": "我想买一台三星手机",
        "should_save": False,
    },

    # =========================
    # ② 长期品牌偏好
    # =========================
    {
        "id": "002",
        "query": "我一直喜欢三星手机",
        "should_save": True,
    },

    # =========================
    # ③ 一次性预算
    # =========================
    {
        "id": "003",
        "query": "这次买手机预算5000元",
        "should_save": False,
    },

    # =========================
    # ④ 长期预算
    # =========================
    {
        "id": "004",
        "query": "我买手机通常预算5000元左右",
        "should_save": True,
    },

    # =========================
    # ⑤ 长期习惯
    # =========================
    {
        "id": "005",
        "query": "我平时跑步",
        "should_save": True,
    },

    # =========================
    # ⑥ 一次性行为
    # =========================
    {
        "id": "006",
        "query": "我今天跑了5公里",
        "should_save": False,
    },

    # =========================
    # ⑦ 长期购买偏好
    # =========================
    {
        "id": "007",
        "query": "我买耳机比较看重降噪",
        "should_save": True,
    },

    # =========================
    # ⑧ 当前搜索需求
    # =========================
    {
        "id": "008",
        "query": "帮我找一个降噪耳机",
        "should_save": False,
    },

    # =========================
    # ⑨ 多个独立事实
    # =========================
    {
        "id": "009",
        "query": "我喜欢三星手机，而且比较看重拍照",
        "should_save": True,
        "max_memories": 1,
    },

    # =========================
    # ⑩ 临时场景 + 临时预算
    # =========================
    {
        "id": "010",
        "query": "我今天去买三星手机，预算5000元",
        "should_save": False,
    },

    # =========================
    # ⑪ 不确定的未来偏好
    # =========================
    {
        "id": "011",
        "query": "我可能以后会喜欢苹果手机",
        "should_save": False,
    },

    # =========================
    # ⑫ 长期场景 + 长期偏好
    # =========================
    {
        "id": "012",
        "query": "我经常出差，所以比较重视手机续航",
        "should_save": True,
    },
]


async def run_case(case):
    print("\n" + "=" * 70)
    print(f"CASE {case['id']}")
    print(f"Query: {case['query']}")
    print(f"Expected save: {case['should_save']}")

    state = {
        "user_id": f"boundary_{case['id']}",
        "messages": [
            HumanMessage(content=case["query"])
        ],
        "memories": [],
    }

    try:
        result = await memory_write_node(state)

        print("Node result:", result)

    except Exception as e:
        print(f"❌ Node Error: {type(e).__name__}: {e}")


def check_database():
    print("\n\n")
    print("=" * 70)
    print("DATABASE RESULT")
    print("=" * 70)

    db = SessionLocal()

    try:
        memories = (
            db.query(Memory)
            .filter(Memory.user_id.like("boundary_%"))
            .order_by(Memory.user_id)
            .all()
        )

        if not memories:
            print("没有保存任何 Memory")
            return

        for memory in memories:
            print(
                f"\nuser_id     : {memory.user_id}"
                f"\ncontent     : {memory.content}"
                f"\nmemory_type : {memory.memory_type}"
                f"\nimportance  : {memory.importance}"
            )

    finally:
        db.close()


async def main():
    print("=" * 70)
    print("Memory Write Boundary Test")
    print("=" * 70)

    # 依次执行所有 Case
    for case in TEST_CASES:
        await run_case(case)

    # 最后统一查看数据库
    check_database()


if __name__ == "__main__":
    asyncio.run(main())