"""Trains the expense forecasting models and saves them to models/.

Run from the SmartSpend root:
    python ml/expense_forecasting/train.py
"""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

try:  # imported as part of the ml package (e.g. by the backend)
    from .features import CATEGORICAL, FEATURES, add_features, complete_months
except ImportError:  # run directly as a script
    from features import CATEGORICAL, FEATURES, add_features, complete_months

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "dataset" / "monthly_spending.csv"
MODEL_PATH = BASE_DIR / "models" / "expense_forecaster.joblib"

QUANTILES = (0.1, 0.5, 0.9)   # low / expected / high
HOLDOUT_MONTHS = 6


def wape(y, p):
    return np.abs(y - p).sum() / y.sum()


def fit_models(rows):
    """One model per quantile. The 0.5 model is the expected value and, being a median
    model, ignores one-off spikes (a wedding, a medical bill) instead of chasing them."""
    return {
        q: HistGradientBoostingRegressor(
            loss="quantile", quantile=q, categorical_features=CATEGORICAL, random_state=42
        ).fit(rows[FEATURES], rows["target"])
        for q in QUANTILES
    }


def main():
    df = complete_months(pd.read_csv(DATA_PATH))
    categories = sorted(df["category"].unique())
    data = add_features(df, categories)
    data = data.dropna(subset=FEATURES + ["target"])

    # 1) honest check: train on the past, test on the most recent months
    cutoff = data["month"].max() - pd.DateOffset(months=HOLDOUT_MONTHS - 1)
    train, test = data[data["month"] < cutoff], data[data["month"] >= cutoff].copy()
    models = fit_models(train)
    ratios = np.sort(np.column_stack([models[q].predict(test[FEATURES]) for q in QUANTILES]), axis=1)
    low, mid, high = (ratios * test["avg12"].to_numpy()[:, None]).T

    print(f"Holdout: {cutoff.date()} onwards ({len(test)} rows)")
    print(f"  Model WAPE:            {wape(test['amount'], mid):.4f}")
    print(f"  12-month-average WAPE: {wape(test['amount'], test['avg12']):.4f}")
    print(f"  Actual inside range:   {((test['amount'] >= low) & (test['amount'] <= high)).mean():.1%}")

    # 2) final models: retrain on ALL data so they know about the latest months
    final_models = fit_models(data)
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump({"models": final_models, "categories": categories}, MODEL_PATH)
    print(f"\nModel saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()
