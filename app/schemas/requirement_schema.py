from pydantic import BaseModel
from typing import Optional

class Requirements(BaseModel):
    category:str
    brand:Optional[str] = None
    description:Optional[str] = None
    price_max:Optional[float] = None
    price_min:Optional[float] = None
    price_preference: Optional[str] = None
    sizes:Optional[str] = None
    storage:Optional[str] = None
    color:Optional[list[str]] = None
    tags:Optional[list[str]] = None