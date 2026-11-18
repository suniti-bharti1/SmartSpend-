from collections import defaultdict
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.database import get_db
from app.models import User, Transaction
from app.dependencies import get_current_user
from app.services.ml_service import forecast_for_user

router=APIRouter(prefix="/api/analytics",tags=["Analytics & Forecasting"])
@router.get("/summary")
def summary(month: str | None=None, user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    q=db.query(Transaction).filter(Transaction.user_id==user.id)
    if month:
        q=q.filter(func.to_char(Transaction.date,"YYYY-MM")==month)
    income=q.filter(Transaction.transaction_type=="income").with_entities(func.coalesce(func.sum(Transaction.amount),0)).scalar()
    expenses=q.filter(Transaction.transaction_type=="expense").with_entities(func.coalesce(func.sum(Transaction.amount),0)).scalar()
    return {"income":float(income),"expenses":float(expenses),"balance":float(income-expenses),"month":month}
@router.get("/monthly")
def monthly(user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    rows=db.query(func.to_char(Transaction.date,"YYYY-MM").label("month"),Transaction.transaction_type,func.sum(Transaction.amount).label("total")).filter(Transaction.user_id==user.id).group_by("month",Transaction.transaction_type).order_by("month").all()
    data=defaultdict(lambda:{"income":0.0,"expenses":0.0})
    for r in rows: data[r.month]["income" if r.transaction_type=="income" else "expenses"]=float(r.total)
    return [{"month":m,**v} for m,v in sorted(data.items())]
@router.get("/categories")
def categories(month: str | None=None,user: User=Depends(get_current_user),db: Session=Depends(get_db)):
    q=db.query(Transaction.category,func.sum(Transaction.amount).label("total")).filter(Transaction.user_id==user.id,Transaction.transaction_type=="expense")
    if month: q=q.filter(func.to_char(Transaction.date,"YYYY-MM")==month)
    return [{"category":r.category,"amount":float(r.total)} for r in q.group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).all()]
@router.get("/forecast")
def forecast(user: User=Depends(get_current_user),db: Session=Depends(get_db)):
    rows=db.query(func.to_char(Transaction.date,"YYYY-MM-01").label("month"),Transaction.category,func.sum(Transaction.amount).label("amount")).filter(Transaction.user_id==user.id,Transaction.transaction_type=="expense").group_by("month",Transaction.category).order_by("month").all()
    return forecast_for_user([{"user_id":str(user.id),"month":r.month,"category":r.category,"amount":float(r.amount)} for r in rows])
@router.get("/anomalies")
def anomalies(user: User=Depends(get_current_user),db: Session=Depends(get_db)):
    rows=db.query(Transaction).filter(Transaction.user_id==user.id,Transaction.is_anomaly.is_(True)).order_by(Transaction.date.desc()).limit(100).all()
    return [{"id":r.id,"date":r.date,"description":r.description,"amount":r.amount,"category":r.category,"reason":r.anomaly_reason,"score":r.anomaly_score} for r in rows]
