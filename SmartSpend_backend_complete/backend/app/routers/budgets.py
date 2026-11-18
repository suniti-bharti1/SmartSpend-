from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import User, Budget, Transaction
from app.schemas import BudgetIn
from app.dependencies import get_current_user
router=APIRouter(prefix="/api/budgets",tags=["Budgets"])
@router.post("/",status_code=201)
def create_budget(data:BudgetIn,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    obj=db.query(Budget).filter(Budget.user_id==user.id,Budget.category==data.category,Budget.month==data.month).first()
    if obj: raise HTTPException(409,"A budget for this category and month already exists. Use PUT to update it.")
    obj=Budget(user_id=user.id,**data.model_dump());db.add(obj);db.commit();db.refresh(obj);return {"id":obj.id,"category":obj.category,"month":obj.month,"limit_amount":obj.limit_amount,"spent":0,"remaining":obj.limit_amount}
@router.get("/")
def list_budgets(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    result=[]
    for b in db.query(Budget).filter(Budget.user_id==user.id).all():
        spent=db.query(func.coalesce(func.sum(Transaction.amount),0)).filter(Transaction.user_id==user.id,Transaction.transaction_type=="expense",Transaction.category==b.category,func.to_char(Transaction.date,"YYYY-MM")==b.month).scalar()
        result.append({"id":b.id,"category":b.category,"month":b.month,"limit_amount":b.limit_amount,"spent":float(spent),"remaining":float(b.limit_amount-spent),"percentage":round(float(spent)/b.limit_amount*100,1)})
    return result
@router.put("/{budget_id}")
def update_budget(budget_id:int,data:BudgetIn,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    obj=db.query(Budget).filter(Budget.id==budget_id,Budget.user_id==user.id).first()
    if not obj: raise HTTPException(404,"Budget not found")
    for k,v in data.model_dump().items(): setattr(obj,k,v)
    db.commit();db.refresh(obj);return {"id":obj.id,"category":obj.category,"month":obj.month,"limit_amount":obj.limit_amount}
@router.delete("/{budget_id}")
def delete_budget(budget_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    obj=db.query(Budget).filter(Budget.id==budget_id,Budget.user_id==user.id).first()
    if not obj: raise HTTPException(404,"Budget not found")
    db.delete(obj);db.commit();return {"message":"Budget deleted"}
