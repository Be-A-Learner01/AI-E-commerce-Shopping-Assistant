import asyncio

from app.memory.long_term.service import save_memory
from app.memory.long_term.postgres import SessionLocal
from app.schemas.memory_schema import Memory

#memory 重复边界测试

TEST_CASES = [

    {
        "id": "001",
        "memories": [
            "用户偏好三星手机",
            "用户偏好三星手机",
        ],
        "expected_actions": [
            "create",
            "dedup",
        ],
    },

    {
        "id": "002",
        "memories": [
            "用户喜欢三星手机",
            "用户偏好三星手机",
        ],
        "expected_actions": [
            "create",
            "dedup",
        ],
    },

    {
        "id": "003",
        "memories": [
            "用户一直喜欢三星手机",
            "用户购买手机时偏好三星品牌",
        ],
        "expected_actions": [
            "create",
            "dedup",
        ],
    },

    {
        "id": "004",
        "memories": [
            "用户购买手机比较喜欢三星",
            "用户买手机偏好三星品牌",
        ],
        "expected_actions": [
            "create",
            "dedup",
        ],
    },

    {
        "id": "005",
        "memories": [
            "用户喜欢三星手机",
            "用户喜欢苹果手机",
        ],
        "expected_actions": [
            "create",
            "update",
        ],
    },

    {
        "id": "006",
        "memories": [
            "用户喜欢三星手机",
            "用户购买手机比较看重拍照",
        ],
        "expected_actions": [
            "create",
            "create",
        ],
    },

    {
        "id": "007",
        "memories": [
            "用户购买手机通常预算5000元",
            "用户买手机一般预算5000元",
        ],
        "expected_actions": [
            "create",
            "dedup",
        ],
    },

    {
        "id": "008",
        "memories": [
            "用户购买手机通常预算约5000元",
            "用户购买手机通常预算在5000元左右",
        ],
        "expected_actions": [
            "create",
            "dedup",
        ],
    },

    {
        "id": "009",
        "memories": [
            "用户购买手机通常预算5000元",
            "用户购买手机通常预算8000元",
        ],
        "expected_actions": [
            "create",
            "update",
        ],
    },

    {
        "id": "010",
        "memories": [
            "用户平时经常跑步",
            "用户平时喜欢跑步",
        ],
        "expected_actions": [
            "create",
            "dedup",
        ],
    },
]


async def run_case(case):
    user_id = f"dedup_{case['id']}"

    print("\n" + "=" * 70)
    print(f"CASE {case['id']}")
    print("=" * 70)

    for i, content in enumerate(case["memories"]):
        print(f"\nMemory {i + 1}: {content}")

        result = await save_memory(
            user_id=user_id,
            content=content,
            memory_type="preference",
            importance=0.8,
        )

        actual = result["action"]
        expected = case["expected_actions"][i]

        if actual == expected:
            print(f"Expected: {expected}")
            print(f"Actual  : {actual}")
            print("✅ PASS")
        else:
            print(f"Expected: {expected}")
            print(f"Actual  : {actual}")
            print("❌ FAIL")


def show_database():
    print("\n\n")
    print("=" * 70)
    print("DATABASE RESULT")
    print("=" * 70)

    db = SessionLocal()

    try:
        memories = (
            db.query(Memory)
            .filter(Memory.user_id.like("dedup_%"))
            .order_by(Memory.user_id, Memory.id)
            .all()
        )

        if not memories:
            print("没有 Memory")
            return

        current_user = None

        for memory in memories:

            if memory.user_id != current_user:
                current_user = memory.user_id
                print("\n" + "-" * 60)
                print(f"user_id: {current_user}")

            print(
                f"  id={memory.id}"
                f" | content={memory.content}"
                f" | type={memory.memory_type}"
            )

    finally:
        db.close()


async def main():

    print("=" * 70)
    print("Memory Deduplication Boundary Test")
    print("=" * 70)

    for case in TEST_CASES:
        await run_case(case)

    show_database()


if __name__ == "__main__":
    asyncio.run(main())