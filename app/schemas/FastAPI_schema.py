from pydantic import BaseModel

class ProductResponse(BaseModel):
    id: int
    name: str
    brand: str | None = None
    category: str | None = None
    description: str | None = None
    price: float | None = None
    color: str | None = None
    sizes: list[str] | None = None
    storage: list[str] | None = None
    tags: list[str] | None = None

class ChatResponse(BaseModel):
    status: str
    thread_id: str
    answer: str | None = None
    requirements: dict | None = None
    products: list[ProductResponse] = []
    interrupt: dict | None = None
