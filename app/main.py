from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.agent.graph import create_agent
from app.schemas.FastAPI_schema import ChatResponse
from app.utils.exceptions import LLMError,MemoryError,ProductSearchError
from app.utils.loggings import logger
import uuid


app = FastAPI(title="E-commerce Assistant")

class ChatRequest(BaseModel):
    user_id: str
    query: str
@app.get("/")
async def root():
    return {"message" : "E-commerce Assistant is running"}

@app.post("/chat",response_model=ChatResponse)
async def chat(request: ChatRequest):
    conn = None
    try:
        agent, conn = await create_agent()
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
    except LLMError:
        logger.exception("LLM error")
        raise HTTPException(
            status_code=503,
            detail="AI 服务暂时不可用，请稍后重试"
        )

    except MemoryError:
        logger.exception("Memory error")
        raise HTTPException(
            status_code=503,
            detail="记忆服务暂时不可用，请稍后重试"
        )

    except ProductSearchError:
        logger.exception("Product search error")
        raise HTTPException(
            status_code=503,
            detail="商品搜索服务暂时不可用，请稍后重试"
        )

    except Exception:
        logger.exception("Unexpected API error")
        raise HTTPException(
            status_code=500,
            detail="服务器内部错误"
        )

    finally:
        if conn is not None:
            await conn.close()

