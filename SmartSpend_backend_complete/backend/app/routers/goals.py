from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User,Goal
from app.schemas import GoalIn,ContributionIn
from app.dependencies import get_current_user
router=APIRouter(prefix="/api/goals",tags=["Financial Goals"])
def pack(g): return {"id":g.id,"title":g.title,"target_amount":g.target_amount,"saved_amount":g.saved_amount,"remaining":max(0,g.target_amount-g.saved_amount),"progress":round(min(100,g.saved_amount/g.target_amount*100),1),"target_date":g.target_date}
@router.post("/",status_code=201)
def create_goal(data:GoalIn,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    g=Goal(user_id=user.id,**data.model_dump());db.add(g);db.commit();db.refresh(g);return pack(g)
@router.get("/")
def list_goals(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    return [pack(g) for g in db.query(Goal).filter(Goal.user_id==user.id).order_by(Goal.id.desc()).all()]
@router.patch("/{goal_id}/contribute")
def contribute(goal_id:int,data:ContributionIn,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    g=db.query(Goal).filter(Goal.id==goal_id,Goal.user_id==user.id).first()
    if not g: raise HTTPException(404,"Goal not found")
    g.saved_amount += data.amount;db.commit();db.refresh(g);return pack(g)
@router.delete("/{goal_id}")
def delete_goal(goal_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    g=db.query(Goal).filter(Goal.id==goal_id,Goal.user_id==user.id).first()
    if not g: raise HTTPException(404,"Goal not found")
    db.delete(g);db.commit();return {"message":"Goal deleted"}
