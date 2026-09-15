from pydantic import BaseModel,field_validator
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

    @field_validator("*", mode="before")
    @classmethod
    def normalize_null(cls,value):
        if value == "null":
            return None
        return value