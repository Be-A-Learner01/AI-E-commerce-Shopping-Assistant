from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage
from app.agent.graph import create_agent
from app.schemas.FastAPI_schema import ChatResponse
from app.utils.exceptions import LLMError,MemoryError,ProductSearchError
from app.utils.loggings import logger
import uuid
import json


app = FastAPI(title="E-commerce Assistant")

class ChatRequest(BaseModel):
    user_id: str = Field(...,min_length=1)
    query: str = Field(...,min_length=1)
@app.get("/")
async def root():
    return {"message" : "E-commerce Assistant is running"}

@app.post("/chat",response_model=ChatResponse)
async def chat(request: ChatRequest):
    thread_id = str(uuid.uuid4())
    conn = None

    try:
        agent, conn = await create_agent()

        result = await agent.ainvoke(
            {
                "user_id": request.user_id,
                "messages": [
                    HumanMessage(content=request.query)
                ],
            },
            config={
                "configurable":{
                    "thread_id":thread_id
                }
            }
        )
        messages = result.get("messages", [])
        answer = None

        for message in reversed(messages):
            if isinstance(message, AIMessage) and message.content:
                    answer = message.content
                    break
        products = []

        for message in messages:

            if (
                    isinstance(message, ToolMessage)
                    and message.name == "search_products"
            ):

                tool_result = message.content

                # ToolMessage.content 可能是 JSON 字符串
                if isinstance(tool_result, str):
                    tool_result = json.loads(tool_result)

                products = tool_result.get(
                    "products",
                    []
                )

                break
        # 展示 requirements 和 products
        return {
            "answer": answer,
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

