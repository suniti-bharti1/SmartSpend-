# Expense Assistant

Chat assistant for the expense tracker. Answers questions about
biggest expense, budget remaining, and savings needed.

## Setup
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
```

## API
POST /chat
Send:    {"user_id": "u1", "message": "How much of my budget is left?"}
Receive: {"reply": "..."}

## For the backend teammate
Replace the functions in data.py with real database queries.
Keep the same function names and return shapes. Take user_id
from the logged-in session, not from the request body.

## For the frontend teammate
Build the chat bubble to call POST /chat and show the reply.