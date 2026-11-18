# SmartSpend Backend

Backend API for the SmartSpend personal finance and expense management system, built using FastAPI and PostgreSQL.

## Technologies Used

- Python 3.13
- FastAPI
- Uvicorn
- PostgreSQL
- SQLAlchemy
- Pydantic
- Psycopg
- Argon2 password hashing

## Project Structure

```text
SmartSpend_Backend/
│
├── main.py
├── database.py
├── models.py
├── requirements.txt
├── .env
├── .gitignore
│
├── routers/
│   ├── __init__.py
│   ├── users.py
│   ├── categories.py
│   ├── transactions.py
│   ├── budgets.py
│   └── savings_goals.py
│
└── schemas/
    ├── __init__.py
    ├── users.py
    ├── categories.py
    ├── transaction.py
    ├── budget.py
    └── savings_goal.py
```

## Setup Instructions

### 1. Install prerequisites

Install Python 3.13 and PostgreSQL.

### 2. Open the project folder

Open Windows CMD and navigate to the project directory:

```cmd
cd SmartSpend_Backend
```

### 3. Create a virtual environment

```cmd
python -m venv venv
```

Activate it:

```cmd
venv\Scripts\activate
```

### 4. Install dependencies

```cmd
pip install -r requirements.txt
```

### 5. Configure the database

Create a `.env` file in the project root.

Add your own PostgreSQL connection string:

```env
DATABASE_URL=postgresql+psycopg://USERNAME:PASSWORD@localhost:5432/DATABASE_NAME
```

Replace the placeholders with your PostgreSQL username, password, and database name.

Ensure the PostgreSQL database and required tables exist. The project uses these tables:

- users
- categories
- transactions
- budgets
- savings_goals

Do not share your `.env` file or commit it to Git.

### 6. Run the backend server

```cmd
uvicorn main:app --host 127.0.0.1 --port 8002
```

Keep the CMD window running while using the API.

### 7. Open API documentation

Visit:

http://127.0.0.1:8002/docs

This opens Swagger UI, where you can view and test the available API endpoints.

## Available API Routes

| Module | Endpoint |
|---|---|
| Users | `/users/` |
| Categories | `/categories/` |
| Transactions | `/transactions/` |
| Budgets | `/budgets/` |
| Savings Goals | `/savings-goals/` |
| Database Test | `/test-db` |
| Health Check | `/health` |

Refer to Swagger UI for the available HTTP methods and additional routes.

## Important Notes

- Keep PostgreSQL running before starting the backend.
- Configure your own `.env` file.
- Never commit database credentials or passwords.
- The database tables must exist before the application accesses them.
- For production, configure CORS to allow only trusted frontend origins.