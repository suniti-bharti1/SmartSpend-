"""Shared feature engineering for training and prediction."""
import numpy as np
import pandas as pd

ML_FEATURES = ["log_ratio", "hour", "is_night"]
MIN_HISTORY = 5  # need at least this many past payments in a category to trust a user's own median


def add_features(df, global_medians=None):
    """Adds typical, log_ratio, is_night and is_repeat columns.

    typical    = this user's median amount in this category (falls back to the
                 all-user category median when the user has too little history)
    log_ratio  = log(amount / typical); 0 = normal, ~2 = about 7x bigger
    is_repeat  = same user, date, merchant and amount already appeared earlier
    """
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"])

    grp = out.groupby(["user_id", "category"])["amount"]
    typical = grp.transform("median")
    count = grp.transform("count")
    if global_medians is not None:
        fallback = out["category"].map(global_medians)
        typical = typical.where(count >= MIN_HISTORY, fallback)
        typical = typical.fillna(out["amount"].median())  # category never seen before
    out["typical"] = typical

    out["log_ratio"] = np.log(np.maximum(out["amount"], 1) / np.maximum(typical, 1))
    out["is_night"] = out["hour"].between(0, 5).astype(int)
    out["is_repeat"] = (
        out.groupby(["user_id", "date", "description", "amount"]).cumcount() > 0
    ).astype(int)
    return out