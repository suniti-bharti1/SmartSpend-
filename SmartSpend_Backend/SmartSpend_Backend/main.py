
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from database import engine

# Import all routers
from routers import categories
from routers import users
from routers import transactions
from routers import budgets
from routers import savings_goals


# Create FastAPI application
app = FastAPI(
    title="SmartSpend API",
    description="Backend API for SmartSpend Expense Management System",
    version="1.0.0"
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register all routers
app.include_router(categories.router)
app.include_router(users.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(savings_goals.router)


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to SmartSpend API!",
        "status": "Running successfully"
    }


# Database connection test
@app.get("/test-db")
def check_database():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "message": "PostgreSQL connected successfully!",
            "status": "Connected"
        }

    except Exception as e:
        return {"error": str(e)}


# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "Healthy"
    }
