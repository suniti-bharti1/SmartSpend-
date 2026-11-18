from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.config import settings
from app.routers import auth, transactions, analytics, budgets, goals, ai

Base.metadata.create_all(bind=engine)
app=FastAPI(title="SmartSpend API",version="1.0.0",description="SmartSpend financial analytics and ML backend")
app.add_middleware(CORSMiddleware,allow_origins=[settings.frontend_origin],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
for router in [auth.router,transactions.router,analytics.router,budgets.router,goals.router,ai.router]: app.include_router(router)
@app.get("/")
def root(): return {"message":"SmartSpend API is running","docs":"/docs"}
@app.get("/health")
def health(): return {"status":"ok"}
