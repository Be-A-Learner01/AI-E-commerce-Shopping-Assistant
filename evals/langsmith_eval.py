from langsmith import Client
from dotenv import load_dotenv
import asyncio
from app.agent.graph import create_agent
from evals.evaluators import evaluate_requirements
from langsmith.evaluation import aevaluate
from langchain_core.messages import HumanMessage
import uuid

client = Client()

load_dotenv()
# 1："c1c02bf6-4a55-466e-baf6-03a9378220b6"
# 2: "41d484c0-3e20-473b-b04f-86c4b8e4afa3"
DATASET_ID = "84cc84ba-979c-4967-8ecc-82f6fc39d828"


def evaluator(run, example):
    predicted = run.outputs["requirements"]
    expected = example.outputs

    result = evaluate_requirements(predicted,expected)

    print("=== Evaluation Debug ===")
    print("Predicted:", predicted)
    print("Expected:", expected)
    print("Details:", result)

    return {
        "key": "requirements_accuracy",
        "score": result["accuracy"],
        "results": result["results"]
    }

async def target(inputs):
    agent, conn = await create_agent()

    try:
        result = await agent.ainvoke({
            "query": inputs["query"],
            "messages": [
                HumanMessage(content=inputs["query"])
            ]
        },
        config={
            "configurable": {
                "thread_id": str(uuid.uuid4())
            }
        }
    )
        return {
            "requirements": result["requirements"]
        }

    finally:
        await conn.close()

async def main():
    results = await aevaluate(
        target,
        data=DATASET_ID,
        evaluators=[evaluator],
        experiment_prefix="e-assi-requirements",
        max_concurrency=1,
    )
    print(results)

if __name__ == "__main__":
    asyncio.run(main())