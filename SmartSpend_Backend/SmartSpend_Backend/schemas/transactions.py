
from pydantic import BaseModel, ConfigDict
from datetime import date
from decimal import Decimal
from typing import Optional


class TransactionCreate(BaseModel):
    user_id: int
    category_id: Optional[int] = None
    description: Optional[str] = None
    amount: Decimal
    transaction_date: date
    transaction_type: str


class TransactionResponse(BaseModel):
    transaction_id: int
    user_id: int
    category_id: Optional[int] = None
    description: Optional[str] = None
    amount: Decimal
    transaction_date: date
    transaction_type: str

    model_config = ConfigDict(from_attributes=True)


class TransactionUpdate(BaseModel):
    category_id: Optional[int] = None
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    transaction_date: Optional[date] = None
    transaction_type: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
