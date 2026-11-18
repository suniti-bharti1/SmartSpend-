"""Forecasts next month's spending per category, with a likely range.

Use from other code:
    from predict import forecast_next_month, forecast_totals
    fc = forecast_next_month(monthly_history_dataframe)   # one or many users
    forecast_totals(fc)

Demo from the terminal:
    python ml/expense_forecasting/predict.py

Input columns: user_id, month, category, amount   (amount = total spent in that month)
Output columns: user_id, category, month, low, expected, high, method
"""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

try:  # imported as part of the ml package (e.g. by the backend)
    from .features import FEATURES, REQUIRED, add_features, complete_months
except ImportError:  # run directly as a script
    from features import FEATURES, REQUIRED, add_features, complete_months

MODEL_PATH = Path(__file__).resolve().parent / "models" / "expense_forecaster.joblib"
MIN_HISTORY_FALLBACK = 3   # below this many months, we don't forecast at all
QUANTILES = (0.1, 0.5, 0.9)

_artifact = None


def _load():
    global _artifact
    if _artifact is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"No trained model at {MODEL_PATH}. Run train.py first.")
        _artifact = joblib.load(MODEL_PATH)
    return _artifact


def forecast_next_month(history):
    """Forecasts the month after each user's latest month of history.

    method = "model"    -> at least 12 months of history: full ML forecast
    method = "fallback" -> 3 to 11 months: median of recent months, range = recent min..max
    Series with fewer than 3 months of history are left out.
    """
    missing = [c for c in REQUIRED if c not in history.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    art = _load()
    full = complete_months(history)

    # add one empty row per series for the month we want to predict
    last = full.groupby("user_id")["month"].max()
    future = full[["user_id", "category"]].drop_duplicates().reset_index(drop=True)
    future["month"] = future["user_id"].map(last) + pd.DateOffset(months=1)
    future["amount"] = np.nan

    feat = add_features(pd.concat([full, future], ignore_index=True), art["categories"])
    g = feat.groupby(["user_id", "category"])["amount"]
    for name, fn in {"fb_low": "min", "fb_mid": "median", "fb_high": "max"}.items():
        feat[name] = g.transform(lambda s, fn=fn: getattr(s.shift(1).rolling(6, min_periods=3), fn)())

    rows = feat[feat["amount"].isna()].copy()
    rows = rows[rows["n_hist"] >= MIN_HISTORY_FALLBACK]

    # cat_code may be empty for a category the model never saw; the model treats that as
    # "unknown category", so only the numeric features must be present to use the model
    can_model = rows[[f for f in FEATURES if f != "cat_code"]].notna().all(axis=1)
    rows["low"], rows["expected"], rows["high"] = rows["fb_low"], rows["fb_mid"], rows["fb_high"]
    rows["method"] = "fallback"

    if can_model.any():
        m = rows[can_model]
        ratios = np.sort(np.column_stack([art["models"][q].predict(m[FEATURES]) for q in QUANTILES]), axis=1)
        scaled = ratios * m["avg12"].to_numpy()[:, None]
        rows.loc[can_model, ["low", "expected", "high"]] = scaled
        rows.loc[can_model, "method"] = "model"

    out = rows[["user_id", "category", "month", "low", "expected", "high", "method"]].copy()
    out[["low", "expected", "high"]] = out[["low", "expected", "high"]].clip(lower=0).round(0)
    return out.sort_values(["user_id", "category"]).reset_index(drop=True)


def forecast_totals(forecast):
    """Total expected spend per user. Sums the 'expected' values only: adding up every
    category's low and high would give a uselessly wide range, because categories
    do not all hit their extremes in the same month."""
    return forecast.groupby(["user_id", "month"], as_index=False)["expected"].sum()


if __name__ == "__main__":
    data = pd.read_csv(Path(__file__).resolve().parent / "dataset" / "monthly_spending.csv")

    u1 = data[data["user_id"] == "U01"]
    fc = forecast_next_month(u1)
    print("U01 forecast for", fc["month"].iloc[0].strftime("%B %Y"))
    print(fc[["category", "low", "expected", "high", "method"]].to_string(index=False))
    print("\nExpected total:", int(forecast_totals(fc)["expected"].iloc[0]))

    # a newer user with only 4 months of history -> uses the fallback method
    new_user = u1[pd.to_datetime(u1["month"]) >= "2026-07-01"].assign(user_id="NEW")
    print("\nNew user (4 months of history):")
    print(forecast_next_month(new_user)[["category", "low", "expected", "high", "method"]].head(4).to_string(index=False))
