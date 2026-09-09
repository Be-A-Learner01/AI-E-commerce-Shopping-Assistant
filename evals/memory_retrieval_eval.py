
from app.memory.long_term.postgres import SessionLocal
from app.memory.long_term.repository import search_memories


TEST_CASES = [
    {
        "name": "三星手机",
        "query": "我想买一台三星手机",
        "relevant_keywords": ["三星"],
    },
    {
        "name": "推荐手机",
        "query": "给我推荐一台手机",
        "relevant_keywords": ["三星", "8000"],
    },
    {
        "name": "跑鞋",
        "query": "我想买一双跑鞋",
        "relevant_keywords": [],
    },
]
TOP_K = 5
SIMILARITY_THRESHOLD = 0.6

def is_relevant(content:str,keywords:list[str]) -> bool:
    """
    判断 memory 是否和当前的query 相关
    """
    if not keywords:
        return False
    return  any(keyword in content for keyword in keywords)

def evaluate_case(case):
    db = SessionLocal()

    try:
        memories = search_memories(
            db=db,
            user_id="test001",
            query=case["query"],
            top_k=TOP_K,
            threshold = SIMILARITY_THRESHOLD
        )
        retrieved_content = [memory.content for memory,distance in memories]
        relevant_retrieved = [content for content in retrieved_content
                              if is_relevant(content,case["relevant_keywords"])]

        retrieved_count = len(retrieved_content)
        relevant_count = len(relevant_retrieved)

        if retrieved_count == 0:
            precision = 0.0
        else:
            precision = relevant_count/retrieved_count

        if case["relevant_keywords"]:
            recall = 1.0 if relevant_count > 0 else 0.0
        else:
            recall = 1.0 if relevant_count == 0 else 0.0
        print("\n====================")
        print(f"Case: {case['name']}")
        print(f"Query: {case['query']}")
        print("\nRetrieved:")

        for i,content in enumerate(retrieved_content,1):
            print(f"{i}, {content}")

        print("\nMetrics:")
        print(f"Precision@{TOP_K}: {precision:.2f}")
        print(f"Recall@{TOP_K}: {recall:.2f}")

        return {
            "precision":precision,
            "recall":recall
        }

    finally:
        db.close()
def main():
    total_precision = 0
    total_recall = 0

    for case in TEST_CASES:
        result = evaluate_case(case)

        total_precision += result["precision"]
        total_recall += result["recall"]
    count = len(TEST_CASES)
    avg_precision = total_precision/count
    avg_recall = total_recall/count

    print("\n====================")
    print("Final Evaluation")
    print("====================")

    print(f"Average Precision@{TOP_K}: {avg_precision:.2f}")
    print(f"Average Recall@{TOP_K}: {avg_recall:.2f}")


if __name__ == "__main__":
        main()