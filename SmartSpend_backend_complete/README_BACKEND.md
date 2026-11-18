# SmartSpend Backend (FastAPI + PostgreSQL + existing ML models)

## Included
- FastAPI REST API, SQLAlchemy models and PostgreSQL connection
- JWT registration/login and protected routes
- Transaction CRUD and CSV import (UTF-8 CSV, date/description/amount or debit/credit)
- Existing expense categorization, anomaly detection and forecasting models from your uploaded SmartSpend ZIP
- Monthly/category analytics, anomaly listing, budgets and savings goals
- Dockerfile and docker-compose PostgreSQL + API setup

## 1. Important: keep the folder structure
The `ml/` directory in this package is copied from your uploaded project, including its trained `.joblib` files. Keep it beside `backend/`:

```
SmartSpend/
  ml/
  backend/
  docker-compose.yml
```

Do not copy your old `venv/` folder. Create a new virtual environment for this backend.

## 2. Local Windows setup
From the SmartSpend project root (the folder containing `ml` and `backend`):

```powershell
py -3.11 -m venv backendenv
backendenv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backendequirements.txt
Copy-Item backend\.env.example backend\.env
```

Edit `backend/.env`, set your local PostgreSQL password and replace `SECRET_KEY` with a long random value. Create the database once in pgAdmin or psql:

```sql
CREATE DATABASE smartspend;
```

Run from the project root:

```powershell
$env:PYTHONPATH = "$PWD;$PWDackend"
uvicorn app.main:app --app-dir backend --reload
```

Open http://127.0.0.1:8000/docs

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again.

## 3. Docker setup
From the project root run:

```bash
docker compose up --build
```

API: http://localhost:8000/docs. Docker compose starts PostgreSQL and API. For deployment, change the default database password and secret key.

## 4. API flow
1. `POST /api/auth/register`
2. `POST /api/auth/login` and click **Authorize** in Swagger; enter the returned token as `Bearer <token>` if Swagger does not prefill it.
3. `POST /api/transactions/` or `POST /api/transactions/upload`
4. Test `/api/analytics/summary`, `/monthly`, `/categories`, `/forecast`, `/anomalies`
5. Test `/api/budgets/` and `/api/goals/`

Transaction JSON example:
```json
{
  "date": "2026-11-07",
  "hour": 13,
  "description": "Swiggy order",
  "amount": 450,
  "transaction_type": "expense"
}
```

CSV example:
```csv
date,description,amount,transaction_type
2026-11-01,Swiggy order,450,expense
2026-11-02,Monthly salary,30000,income
```

CSV import also accepts `date,description,debit,credit` (fill only one of debit/credit per row). Date should be ISO format `YYYY-MM-DD`.

## 5. Routes
- Auth: `/api/auth/register`, `/api/auth/login`, `/api/auth/me`
- Transactions: `/api/transactions/`, `/api/transactions/upload`, `/api/transactions/{id}`
- Analytics: `/api/analytics/summary`, `/monthly`, `/categories`, `/forecast`, `/anomalies`
- Budgets: `/api/budgets/` GET/POST, `/api/budgets/{id}` PUT/DELETE
- Goals: `/api/goals/` GET/POST, `/api/goals/{id}/contribute`, `/api/goals/{id}` DELETE
- AI: `/api/ai/ask`, `/api/ai/knowledge` are explicit 501 placeholders until the team selects an LLM/embedding provider and API key. These are not implemented live yet.

## 6. ML model notes
The three supplied models are loaded by their original prediction functions. Their own README says they were trained on synthetic data; anomaly flags are not fraud determinations, and forecasts need at least 3 months per category (12 months for the full model). Existing model files must stay in their original `ml/.../models/` paths.

## 7. Current scope / production work still needed
This is a development backend, not a production banking system. Before real users: add Alembic migrations, rate limiting, email verification/password reset, refresh-token strategy, stricter CSV duplicate detection and bank-specific parsers, audit logs, secrets management, backups, and security review. Do not upload real bank credentials or card details.
