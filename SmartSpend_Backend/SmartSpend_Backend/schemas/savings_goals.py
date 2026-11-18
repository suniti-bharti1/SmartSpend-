
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


class SavingsGoalCreate(BaseModel):
    user_id: int
    goal_name: str
    target_amount: Decimal
    current_amount: Optional[Decimal] = 0
    target_date: Optional[date] = None


class SavingsGoalResponse(BaseModel):
    goal_id: int
    user_id: int
    goal_name: str
    target_amount: Decimal
    current_amount: Optional[Decimal] = None
    target_date: Optional[date] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SavingsGoalUpdate(BaseModel):
    goal_name: Optional[str] = None
    target_amount: Optional[Decimal] = None
    current_amount: Optional[Decimal] = None
    target_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)
