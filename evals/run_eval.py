import asyncio
from evals.graders import evaluator
from langsmith import Client
from evals.test_agent import target
from dotenv import load_dotenv


load_dotenv()

client =Client()

async def main():
    results =  await client.aevaluate(
        target,
        data="datasets-e",
        evaluators=[evaluator],
    )
    print(results)


if __name__ == "__main__":
    asyncio.run(main())