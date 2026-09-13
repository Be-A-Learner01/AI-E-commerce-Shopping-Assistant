from pydantic import BaseModel

class ProductResponse(BaseModel):
    id: int
    name: str
    brand: str
    category: str
    description: str | None = None
    price: float
    color:str | None = None
    storage: list[str] | None = None
    tags: list[str] | None = None

class ChatResponse(BaseModel):
    answer: str | None
    requirements: dict
    products: list[ProductResponse]
