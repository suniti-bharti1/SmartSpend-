def get_transactions(user_id):
    return [
        {"category": "Food", "amount": 1500, "date": "2026-11-02"},
        {"category": "Food", "amount": 1000, "date": "2026-11-05"},
        {"category": "Transport", "amount": 800, "date": "2026-11-03"},
        {"category": "Shopping", "amount": 700, "date": "2026-11-04"},
        {"category": "Bills", "amount": 500, "date": "2026-11-01"},
    ]

def get_budget(user_id):
    return 5000

def get_income(user_id):
    return 8000

def get_savings_goal(user_id):
    return 3000