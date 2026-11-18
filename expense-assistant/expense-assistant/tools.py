import json
from collections import defaultdict
import data

def get_top_category(user_id):
    totals = defaultdict(float)
    for t in data.get_transactions(user_id):
        totals[t["category"]] += t["amount"]
    cat = max(totals, key=totals.get)
    return {"category": cat, "amount": totals[cat]}

def get_budget_remaining(user_id):
    spent = sum(t["amount"] for t in data.get_transactions(user_id))
    budget = data.get_budget(user_id)
    return {"budget": budget, "spent": spent, "remaining": budget - spent}

def get_savings_needed(user_id):
    spent = sum(t["amount"] for t in data.get_transactions(user_id))
    saved_so_far = data.get_income(user_id) - spent
    goal = data.get_savings_goal(user_id)
    return {"goal": goal, "saved_so_far": saved_so_far,
            "still_need_to_save": max(0, goal - saved_so_far)}

FUNCS = {
    "get_top_category": get_top_category,
    "get_budget_remaining": get_budget_remaining,
    "get_savings_needed": get_savings_needed,
}

def _tool(name, desc):
    return {"name": name, "description": desc,
            "input_schema": {"type": "object", "properties": {}}}

TOOLS = [
    _tool("get_top_category", "Category with the highest spending, and the amount"),
    _tool("get_budget_remaining", "Monthly budget, amount spent, and amount left"),
    _tool("get_savings_needed", "How much more the user must save to hit their savings goal"),
]

def run_tool(name, user_id):
    return json.dumps(FUNCS[name](user_id))