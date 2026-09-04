from app.agent.graph import agent

async def target(inputs, **kwargs):
    result = await agent.ainvoke({
        "query": inputs["query"]
    })
    return result