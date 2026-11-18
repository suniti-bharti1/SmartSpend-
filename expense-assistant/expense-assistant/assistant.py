import tools

def chat(user_id, message):
    m = message.lower()

    if any(w in m for w in ["most", "biggest", "highest", "top"]):
        r = tools.get_top_category(user_id)
        return f"Your biggest expense is {r['category']}, at ₹{r['amount']:,.0f}."

    if "save" in m or "saving" in m:
        r = tools.get_savings_needed(user_id)
        if r["still_need_to_save"] == 0:
            return "You've already reached your savings goal. Nice work!"
        return (f"To reach your goal of ₹{r['goal']:,.0f}, "
                f"you still need to save ₹{r['still_need_to_save']:,.0f}.")

    if any(w in m for w in ["left", "remaining", "budget"]):
        r = tools.get_budget_remaining(user_id)
        return (f"Your budget is ₹{r['budget']:,.0f}. You've spent "
                f"₹{r['spent']:,.0f}, so ₹{r['remaining']:,.0f} is left.")

    return ("I can help with: your biggest expense, how much budget is left, "
            "and how much you should save. Try asking one of those!")