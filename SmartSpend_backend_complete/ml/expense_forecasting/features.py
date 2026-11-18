"""Shared feature engineering for expense forecasting (training and prediction)."""
import numpy as np
import pandas as pd

FEATURES = ["lag1_r", "lag2_r", "lag3_r", "lag12_r", "avg3_r", "avg6_r",
            "vol_r", "log_level", "cal_month", "cat_code"]
CATEGORICAL = [f in ("cal_month", "cat_code") for f in FEATURES]
REQUIRED = ["user_id", "month", "category", "amount"]


def complete_months(df):
    """Makes every user-category series continuous: a month with no spending becomes 0.

    Without this, a missing month would silently shift all the 'last month / 12 months ago'
    calculations by one position.
    """
    df = df[REQUIRED].copy()
    df["month"] = pd.to_datetime(df["month"]).dt.to_period("M").dt.to_timestamp()
    df = df.groupby(["user_id", "category", "month"], as_index=False)["amount"].sum()

    frames = []
    for user, d in df.groupby("user_id"):
        months = pd.date_range(d["month"].min(), d["month"].max(), freq="MS")
        idx = pd.MultiIndex.from_product(
            [[user], sorted(d["category"].unique()), months],
            names=["user_id", "category", "month"],
        )
        frames.append(d.set_index(["user_id", "category", "month"]).reindex(idx, fill_value=0).reset_index())
    return pd.concat(frames, ignore_index=True)


def add_features(df, categories):
    """Adds features that use ONLY months before each row. Ratios are relative to the
    series' own 12-month average, so small and large spenders share one scale."""
    out = df.sort_values(["user_id", "category", "month"]).reset_index(drop=True)
    g = out.groupby(["user_id", "category"])["amount"]

    out["n_hist"] = g.cumcount()                       # months of history before this row
    out["avg12"] = g.transform(lambda s: s.shift(1).rolling(12).mean()).replace(0, np.nan)
    out["avg6"] = g.transform(lambda s: s.shift(1).rolling(6).mean())
    out["avg3"] = g.transform(lambda s: s.shift(1).rolling(3).mean())
    out["std6"] = g.transform(lambda s: s.shift(1).rolling(6).std())

    for k in (1, 2, 3):
        out[f"lag{k}_r"] = g.shift(k) / out["avg12"]
    out["lag12_r"] = g.shift(12) / out["avg12"]
    out["avg3_r"] = out["avg3"] / out["avg12"]
    out["avg6_r"] = out["avg6"] / out["avg12"]
    out["vol_r"] = out["std6"] / out["avg12"]
    out["log_level"] = np.log(out["avg12"])
    out["cal_month"] = out["month"].dt.month
    out["cat_code"] = out["category"].map({c: i for i, c in enumerate(categories)})
    out["target"] = out["amount"] / out["avg12"]
    return out