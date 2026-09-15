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

    e2e_passed = 0

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
            print("=" * 60)
            print(case["id"])
            print(f"Query: {query}")

            try:
                result = await agent.ainvoke(
                    {
                        "messages":[
                            HumanMessage(content=query)
                        ],
                    },config=config
                )

                requirements = result.get("requirements")
                messages = result.get("messages",[])

                tool_message = next(
                    (
                        message
                        for message in reversed(result["messages"])
                        if isinstance(message, ToolMessage)
                           and message.name == "search_products"
                    ),
                    None
                )

                e2e_checks = {
                    "requirements": requirements is not None,
                    "messages": bool(messages),
                    "tool_result": tool_message is not None,
                }

                e2e_pass = all(e2e_checks.values())

                if e2e_pass:
                    e2e_passed += 1

                print("\nE2E Checks:")

                for name, passed in e2e_checks.items():
                    print(
                        f"{name}: "
                        f"{'PASS' if passed else 'FAIL'}"
                    )

                print(
                    f"E2E Result: "
                    f"{'PASS' if e2e_pass else 'FAIL'}"
                )

                predicted = requirements or {}

                requirement_evals = evaluate_requirements(
                    predicted,
                    expected
                )

                total_requirement_score += (
                    requirement_evals["score"]
                )

                total_requirement_fields += (
                    requirement_evals["total"]
                )

                product_evals = evaluate_product_relevance(tool_message,predicted)

                total_product_score += product_evals["score"]
                total_products += product_evals["total"]

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

            except Exception as e:
                print("\nE2E Result: FAIL")
                print(f"Error: {e}")
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
    e2e_accuracy = (
        e2e_passed / len(dataset)
        if dataset
        else 0
    )

    overall_score = (requirement_accuracy + product_accuracy + e2e_accuracy) / 3

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
        f"E2E Success Rate: "
        f"{e2e_accuracy:.1%}"
    )
    print(
        f"Overall E2E Score: "
        f"{overall_score:.1%}"
    )


if __name__ == "__main__":
    asyncio.run(run_eval())