from datetime import date
import pandas as pd
from ml.expense_categorization.predict import predict_category
from ml.anomaly_detection.predict import check_transaction
from ml.expense_forecasting.predict import forecast_next_month, forecast_totals
from ml.anomaly_detection.predict import REQUIRED as ANOMALY_REQUIRED

def categorize(description: str) -> dict:
    return predict_category(description)

def detect_for_user(new_txn: dict, history_rows: list[dict]) -> dict:
    history = pd.DataFrame(history_rows, columns=ANOMALY_REQUIRED)
    # ML anomaly code expects these six columns even when history is empty.
    if history.empty:
        history = pd.DataFrame(columns=ANOMALY_REQUIRED)
    return check_transaction(new_txn, history)

def forecast_for_user(rows: list[dict]) -> dict:
    if not rows:
        return {"available": False, "message": "Add expense history to generate a forecast.", "items": [], "total_expected": 0}
    monthly = pd.DataFrame(rows)
    if monthly.empty:
        return {"available": False, "message": "No expense history found.", "items": [], "total_expected": 0}
    monthly["month"] = pd.to_datetime(monthly["month"])
    forecast = forecast_next_month(monthly)
    if forecast.empty:
        return {"available": False, "message": "At least 3 months of history per category are required.", "items": [], "total_expected": 0}
    total = forecast_totals(forecast)
    return {"available": True, "items": [{"category": r.category, "month": r.month.strftime("%Y-%m"), "low": float(r.low), "expected": float(r.expected), "high": float(r.high), "method": r.method} for r in forecast.itertuples()], "total_expected": float(total["expected"].sum())}
