
from pydantic import BaseModel, ConfigDict
from decimal import Decimal


class BudgetCreate(BaseModel):
    user_id: int
    category_id: int
    monthly_limit: Decimal
    month: int
    year: int


class BudgetResponse(BaseModel):
    budget_id: int
    user_id: int
    category_id: int
    monthly_limit: Decimal
    month: int
    year: int

    model_config = ConfigDict(from_attributes=True)


class BudgetUpdate(BaseModel):
    monthly_limit: Decimal | None = None
    month: int | None = None
    year: int | None = None

    model_config = ConfigDict(from_attributes=True)
