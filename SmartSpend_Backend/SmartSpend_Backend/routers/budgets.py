
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from decimal import Decimal

from database import get_db
from models import Budget

router = APIRouter(
    prefix="/budgets",
    tags=["Budgets"]
)


class BudgetCreate(BaseModel):
    user_id: int
    category_id: int
    monthly_limit: Decimal
    month: int
    year: int


@router.get("/")
def get_budgets(db: Session = Depends(get_db)):
    return db.query(Budget).all()


@router.get("/user/{user_id}")
def get_user_budgets(
    user_id: int,
    db: Session = Depends(get_db)
):
    return db.query(Budget).filter(
        Budget.user_id == user_id
    ).all()


@router.post("/")
def create_budget(
    budget: BudgetCreate,
    db: Session = Depends(get_db)
):
    new_budget = Budget(**budget.model_dump())

    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)

    return new_budget


@router.delete("/{budget_id}")
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db)
):
    budget = db.query(Budget).filter(
        Budget.budget_id == budget_id
    ).first()

    if not budget:
        raise HTTPException(
            status_code=404,
            detail="Budget not found"
        )

    db.delete(budget)
    db.commit()

    return {"message": "Budget deleted successfully"}
