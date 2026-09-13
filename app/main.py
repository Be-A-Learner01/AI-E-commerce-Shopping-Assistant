from fastapi import FastAPI
from pydantic import BaseModel
from  langchain_core.messages import HumanMessage
from  app.agent.graph import create_agent
import uuid

app = FastAPI(title="E-commerce Assistant")

class ChatRequest(BaseModel):
    user_id: str
    query: str

@app.post("/chat")
async def chat(request: ChatRequest):
    agent,conn = await create_agent()

    try:
        result = await agent.ainvoke(
            {
                "user_id": request.user_id,
                "query": request.query,
                "messages": [
                    HumanMessage(content=request.query)
                ],
            },
            config={
                "configurable":{
                    "thread_id":str(uuid.uuid4())
                }
            }
        )
        products = []

        for item in result.get("products", []):
            product = item["document"].metadata["product"]

            products.append({
                "id": product["id"],
                "name": product["name"],
                "brand": product["brand"],
                "category": product["category"],
                "description": product["description"],
                "price": product["price"],
                "color": product.get("color"),
                "storage": product.get("storage"),
                "tags": product.get("tags"),
            })
        # 展示 requirements 和 products
        return {
            "answer": result.get("answer"),
            "requirements": result.get("requirements"),
            "products": products
        }


    finally:
        await conn.close()

