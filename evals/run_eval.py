import json
from evals.evaluators import evaluate_requirements
from app.agent.graph import create_agent
from dotenv import load_dotenv
import asyncio
from langchain_core.messages import HumanMessage

load_dotenv()

def load_dataset():
    with open("dataset.json","r",encoding="utf-8") as f:
        return json.load(f)

async def run_eval():
    dataset = load_dataset()
    total_score = 0
    total_fields = 0

    for case in dataset:
        query = case["inputs"]["query"]

        expected = case["reference_outputs"]

        agent, conn = await create_agent()

        config = {
            "configurable": {
                "thread_id": case["id"]
            }
        }

        result = await agent.ainvoke(
            {
                "query":query,
                "messages":[
                    HumanMessage(content=query)
                ],
            },config=config
        )

        predicted = result["requirements"]

        scores = evaluate_requirements(predicted,expected)

        total_score += scores["score"]
        total_fields += scores["total"]

        print("=" * 50)
        print(case["id"])
        print("Query:", query)
        print("Expected:", expected)
        print("Predicted:", predicted)
        print("Scores:", scores)
        print(
            f"Score: {scores['score']}/{scores['total']} "
            f"({scores['accuracy']:.1%})"
        )

        await conn.close()

    print("=" * 50)
    print("Overall Evaluation")
    print(f"Score: {total_score}/{total_fields}")
    print(f"Accuracy: {total_score / total_fields:.1%}")

if __name__ == "__main__":
    asyncio.run(run_eval())