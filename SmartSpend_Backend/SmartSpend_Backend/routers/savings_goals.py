
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from decimal import Decimal
from datetime import date

from database import get_db
from models import SavingsGoal

router = APIRouter(
    prefix="/savings-goals",
    tags=["Savings Goals"]
)


class SavingsGoalCreate(BaseModel):
    user_id: int
    goal_name: str
    target_amount: Decimal
    current_amount: Decimal = Decimal("0")
    target_date: date | None = None


@router.get("/")
def get_savings_goals(db: Session = Depends(get_db)):
    return db.query(SavingsGoal).all()


@router.get("/user/{user_id}")
def get_user_savings_goals(
    user_id: int,
    db: Session = Depends(get_db)
):
    return db.query(SavingsGoal).filter(
        SavingsGoal.user_id == user_id
    ).all()


@router.post("/")
def create_savings_goal(
    goal: SavingsGoalCreate,
    db: Session = Depends(get_db)
):
    new_goal = SavingsGoal(**goal.model_dump())

    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)

    return new_goal


@router.delete("/{goal_id}")
def delete_savings_goal(
    goal_id: int,
    db: Session = Depends(get_db)
):
    goal = db.query(SavingsGoal).filter(
        SavingsGoal.goal_id == goal_id
    ).first()

    if not goal:
        raise HTTPException(
            status_code=404,
            detail="Savings goal not found"
        )

    db.delete(goal)
    db.commit()

    return {"message": "Savings goal deleted successfully"}
