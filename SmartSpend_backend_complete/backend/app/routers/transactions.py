from datetime import date
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models import User, Transaction
from app.schemas import TransactionIn, TransactionOut
from app.dependencies import get_current_user
from app.services.ml_service import categorize, detect_for_user
from app.services.csv_service import parse_transactions

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])
def create_one(data: dict, user: User, db: Session) -> Transaction:
    category_info = {"category": data.get("category"), "confidence": None, "needs_review": False}
    if data["transaction_type"] == "expense" and not data.get("category"):
        category_info = categorize(data["description"])
    category = data.get("category") or category_info["category"] or "Other"
    history_rows = [{"user_id": str(user.id), "date": t.date.isoformat(), "hour": t.hour, "description": t.description, "category": t.category, "amount": t.amount}
        for t in db.query(Transaction).filter(Transaction.user_id == user.id, Transaction.transaction_type == "expense").order_by(desc(Transaction.date)).limit(500).all()]
    anomaly = {"is_anomaly": False, "reason": "", "score": None}
    if data["transaction_type"] == "expense":
        txn = {"user_id": str(user.id), "date": data["date"].isoformat(), "hour": data.get("hour", 12), "description": data["description"], "category": category, "amount": data["amount"]}
        anomaly = detect_for_user(txn, history_rows)
    obj = Transaction(user_id=user.id, date=data["date"], hour=data.get("hour",12), description=data["description"], amount=data["amount"], transaction_type=data["transaction_type"], category=category, category_confidence=category_info.get("confidence"), needs_review=category_info.get("needs_review",False), is_anomaly=anomaly["is_anomaly"], anomaly_reason=anomaly.get("reason") or None, anomaly_score=anomaly.get("score"))
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.post("/", response_model=TransactionOut, status_code=201)
def add_transaction(data: TransactionIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_one(data.model_dump(), user, db)
@router.get("/", response_model=list[TransactionOut])
def list_transactions(start_date: date | None = None, end_date: date | None = None, transaction_type: str | None = Query(default=None, pattern="^(income|expense)$"), limit: int = Query(default=100, ge=1, le=1000), offset: int = Query(default=0, ge=0), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Transaction).filter(Transaction.user_id == user.id)
    if start_date: q=q.filter(Transaction.date >= start_date)
    if end_date: q=q.filter(Transaction.date <= end_date)
    if transaction_type: q=q.filter(Transaction.transaction_type == transaction_type)
    return q.order_by(desc(Transaction.date), desc(Transaction.id)).offset(offset).limit(limit).all()
@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(transaction_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    obj=db.query(Transaction).filter(Transaction.id==transaction_id, Transaction.user_id==user.id).first()
    if not obj: raise HTTPException(404,"Transaction not found")
    return obj
@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    obj=db.query(Transaction).filter(Transaction.id==transaction_id, Transaction.user_id==user.id).first()
    if not obj: raise HTTPException(404,"Transaction not found")
    db.delete(obj); db.commit(); return {"message":"Transaction deleted"}
@router.post("/upload", tags=["CSV Import"])
async def upload_csv(file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(400,"Please upload a .csv file")
    raw=await file.read()
    if len(raw)>5*1024*1024: raise HTTPException(413,"CSV file must be 5 MB or smaller")
    rows=parse_transactions(raw)
    created=[]
    try:
        for row in rows:
            created.append(create_one(row,user,db).id)
    except Exception:
        db.rollback(); raise
    return {"message":"CSV imported successfully","imported_count":len(created),"transaction_ids":created}
