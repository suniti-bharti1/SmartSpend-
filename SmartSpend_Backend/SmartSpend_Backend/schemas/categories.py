
from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    category_name: str
    category_type: str


class CategoryResponse(BaseModel):
    category_id: int
    category_name: str
    category_type: str

    model_config = ConfigDict(from_attributes=True)


class CategoryUpdate(BaseModel):
    category_name: str | None = None
    category_type: str | None = None

    model_config = ConfigDict(from_attributes=True)
