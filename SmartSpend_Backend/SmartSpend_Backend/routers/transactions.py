
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from decimal import Decimal
from datetime import date

from database import get_db
from models import Transaction

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

class TransactionCreate(BaseModel):
    user_id: int
    category_id: int | None = None
    description: str | None = None
    amount: Decimal
    transaction_date: date
    transaction_type: str

# Get all transactions
@router.get("/")
def get_transactions(db: Session = Depends(get_db)):
    return db.query(Transaction).all()

# Get transactions of a particular user
@router.get("/user/{user_id}")
def get_user_transactions(
    user_id: int,
    db: Session = Depends(get_db)
):
    return db.query(Transaction).filter(
        Transaction.user_id == user_id
    ).order_by(Transaction.transaction_date.desc()).all()

# Add a new transaction
@router.post("/")
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    new_transaction = Transaction(**transaction.model_dump())

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction

# Delete a transaction
@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    transaction = db.query(Transaction).filter(
        Transaction.transaction_id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    db.delete(transaction)
    db.commit()

    return {"message": "Transaction deleted successfully"}