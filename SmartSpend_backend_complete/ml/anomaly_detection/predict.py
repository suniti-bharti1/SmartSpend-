"""Flags unusual transactions using a hybrid of a rule and an Isolation Forest.

Use from other code:
    from predict import check_transaction, detect_anomalies
    check_transaction(new_txn_dict, user_history_dataframe)
    detect_anomalies(dataframe_of_transactions)

Demo from the terminal:
    python ml/anomaly_detection/predict.py

Required columns: user_id, date, hour, description, category, amount
"""
from pathlib import Path

import joblib
import pandas as pd

try:  # imported as part of the ml package (e.g. by the backend)
    from .features import ML_FEATURES, add_features
except ImportError:  # run directly as a script
    from features import ML_FEATURES, add_features

MODEL_PATH = Path(__file__).resolve().parent / "models" / "anomaly_detector.joblib"
REQUIRED = ["user_id", "date", "hour", "description", "category", "amount"]

_artifact = None


def _load():
    global _artifact
    if _artifact is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"No trained model at {MODEL_PATH}. Run train.py first.")
        _artifact = joblib.load(MODEL_PATH)
    return _artifact


def _explain(row):
    reasons = []
    if row["flag_rule"]:
        reasons.append("possible duplicate payment")
    if row["flag_ml"]:
        if row["is_night"]:
            reasons.append("unusual time of day")
        if row["log_ratio"] > 1.0:
            reasons.append("amount much higher than your usual for this category")
        if not any(r != "possible duplicate payment" for r in reasons):
            reasons.append("unusual spending pattern")
    return "; ".join(reasons)


def detect_anomalies(df):
    """Takes a DataFrame of transactions and returns it with is_anomaly_pred, score and reason."""
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    art = _load()
    feat = add_features(df[REQUIRED], art["global_medians"])
    feat["flag_ml"] = art["model"].predict(feat[ML_FEATURES]) == -1
    feat["flag_rule"] = feat["is_repeat"] == 1
    feat["is_anomaly_pred"] = feat["flag_ml"] | feat["flag_rule"]
    feat["score"] = -art["model"].decision_function(feat[ML_FEATURES])  # higher = stranger
    feat["reason"] = feat.apply(_explain, axis=1)
    return feat


def check_transaction(txn, history):
    """Checks one new transaction (dict) against the same user's past transactions (DataFrame)."""
    new = pd.DataFrame([txn])
    combined = pd.concat([history[REQUIRED], new[REQUIRED]], ignore_index=True)
    row = detect_anomalies(combined).iloc[-1]
    return {
        "is_anomaly": bool(row["is_anomaly_pred"]),
        "reason": row["reason"],
        "typical_amount": round(float(row["typical"])),
        "score": round(float(row["score"]), 3),
    }


if __name__ == "__main__":
    data = pd.read_csv(Path(__file__).resolve().parent / "dataset" / "transactions.csv")
    history = data[(data["user_id"] == "U01") & (data["is_anomaly"] == 0)]

    tests = [
        ("Normal lunch", {"hour": 13, "description": "Swiggy", "category": "Food", "amount": 350}),
        ("Huge food bill", {"hour": 14, "description": "Zomato", "category": "Food", "amount": 9000}),
        ("3 AM shopping", {"hour": 3, "description": "Amazon", "category": "Shopping", "amount": 4000}),
        ("Same payment twice", {"hour": 12, "description": "Swiggy", "category": "Food", "amount": 350}),
    ]
    for label, t in tests:
        txn = {"user_id": "U01", "date": "2026-11-05", **t}
        if label == "Same payment twice":  # pretend the identical payment already happened today
            history = pd.concat([history, pd.DataFrame([{**txn, "hour": 11}])], ignore_index=True)
        print(f"{label:20s} -> {check_transaction(txn, history)}")
