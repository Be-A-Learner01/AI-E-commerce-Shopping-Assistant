from langsmith import Client
from dotenv import load_dotenv
from app.agent.graph import create_agent
from evals.evaluators import evaluate_requirements

client = Client()

load_dotenv()

DATASET_ID = "a81dcac8-9997-40b2-8936-456df1c89347"


def evaluator(run, example):
    predicted = run.outputs["requirements"]
    expected = example.outputs

    result = evaluate_requirements(
        predicted,
        expected
    )

    return {
        "key": "requirements_accuracy",
        "score": result["accuracy"],
    }

async def target(inputs):
    agent, conn = await create_agent()

    try:
        result = await agent.ainvoke({
            "query": inputs["query"],
            "messages": [
                {
                    "role": "user",
                    "content": inputs["query"]
                }
            ]
        })

        return {
            "requirements": result["requirements"]
        }

    finally:
        await conn.close()
