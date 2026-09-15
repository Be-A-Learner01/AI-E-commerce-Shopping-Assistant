import json
from evals.requirements_eval import evaluate_requirements
from evals.product_relevance_eval import evaluate_product_relevance
from app.agent.graph import create_agent
from dotenv import load_dotenv
import asyncio
from langchain_core.messages import HumanMessage,ToolMessage

load_dotenv()

def load_dataset():
    with open("dataset.json","r",encoding="utf-8") as f:
        return json.load(f)

async def run_eval():
    dataset = load_dataset()

    total_requirement_score = 0
    total_requirement_fields = 0

    total_product_score = 0
    total_products = 0

    agent, conn = await create_agent()
    try:
        for case in dataset:
            query = case["inputs"]["query"]

            expected = case["reference_outputs"]

            config = {
                "configurable": {
                    "thread_id": case["id"]
                }
            }

            result = await agent.ainvoke(
                {
                    "messages":[
                        HumanMessage(content=query)
                    ],
                },config=config
            )

            predicted = result.get("requirements",{})

            requirement_evals = evaluate_requirements(predicted,expected)

            total_requirement_score += requirement_evals["score"]
            total_requirement_fields += requirement_evals["total"]

            tool_message = next(
                (
                    message
                    for message in reversed(result["messages"])
                    if isinstance(message, ToolMessage)
                       and message.name == "search_products"
                ),
                None
            )

            product_evals = evaluate_product_relevance(
                tool_message,
                predicted
            )

            total_product_score += product_evals["score"]
            total_products += product_evals["total"]

            print("=" * 60)
            print(case["id"])

            print("\nExpected Requirements:")
            print(expected)

            print("\nPredicted Requirements:")
            print(predicted)

            print("\nRequirement Score:")
            print(
                f"{requirement_evals['score']}/"
                f"{requirement_evals['total']}/"
                f"({requirement_evals['accuracy']:.1%})"
            )

            print("\nProduct Score:")
            print(
                f"{product_evals['relevant']}/"
                f"{product_evals['total']}/"
                f"({product_evals['score']:.1%})"
            )

            for message in result["messages"]:
                print(type(message).__name__)
                print(message.content)
    finally:
        await conn.close()

    requirement_accuracy = (
        total_requirement_score / total_requirement_fields
        if total_requirement_fields
        else 0
    )

    product_accuracy = (
        total_product_score / total_products
        if total_products
        else 0
    )

    overall_score = (requirement_accuracy + product_accuracy) / 2

    print("\n" + "=" * 60)
    print("Overall Evaluation")
    print("=" * 60)

    print(
        f"Requirement Accuracy: "
        f"{requirement_accuracy:.1%}"
    )

    print(
        f"Product Relevance: "
        f"{product_accuracy:.1%}"
    )

    print(
        f"Overall E2E Score: "
        f"{overall_score:.1%}"
    )


if __name__ == "__main__":
    asyncio.run(run_eval())