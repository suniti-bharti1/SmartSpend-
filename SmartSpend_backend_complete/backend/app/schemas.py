from datetime import date
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
class LoginIn(BaseModel):
    email: EmailStr
    password: str
class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)
class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
class TransactionIn(BaseModel):
    date: date
    hour: int = Field(default=12, ge=0, le=23)
    description: str = Field(min_length=1, max_length=500)
    amount: float = Field(gt=0)
    transaction_type: str = Field(pattern="^(income|expense)$")
    category: str | None = None
class TransactionOut(BaseModel):
    id: int
    user_id: int
    date: date
    hour: int
    description: str
    amount: float
    transaction_type: str
    category: str
    category_confidence: float | None
    needs_review: bool
    is_anomaly: bool
    anomaly_reason: str | None
    anomaly_score: float | None
    model_config = ConfigDict(from_attributes=True)
class BudgetIn(BaseModel):
    category: str = Field(min_length=1, max_length=80)
    month: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    limit_amount: float = Field(gt=0)
class GoalIn(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    target_amount: float = Field(gt=0)
    target_date: date | None = None
class ContributionIn(BaseModel):
    amount: float = Field(gt=0)
