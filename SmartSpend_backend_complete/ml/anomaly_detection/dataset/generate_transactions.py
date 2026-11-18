"""
Generates synthetic transactions for anomaly detection.
Output: transactions.csv in the same folder as this script.
Columns: user_id, date, hour, description, category, amount, is_anomaly, anomaly_type

NOTE: is_anomaly / anomaly_type are ONLY for grading the model later.

Run from the SmartSpend root:
    python ml/anomaly_detection/dataset/generate_transactions.py
"""
import calendar
import os

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

N_USERS = 30
ANOMALY_RATE = 0.015

# category: (median amount in INR, spread, transactions per month, merchants)
PROFILE = {
    "Food": (350, 0.5, 14, ["Swiggy", "Zomato", "Dominos", "Starbucks", "Chaayos"]),
    "Groceries": (900, 0.5, 8, ["BigBasket", "Blinkit", "Zepto", "DMart"]),
    "Transport": (200, 0.5, 15, ["Uber", "Ola", "Rapido", "Indian Oil"]),
    "Shopping": (1500, 0.7, 4, ["Amazon", "Flipkart", "Myntra", "Ajio"]),
    "Bills & Utilities": (800, 0.4, 3, ["Jio Recharge", "Airtel", "Tata Power", "ACT Fibernet"]),
    "Entertainment": (400, 0.5, 3, ["Netflix", "Spotify", "BookMyShow", "Hotstar"]),
    "Health": (700, 0.7, 2, ["Apollo Pharmacy", "PharmEasy", "Practo", "Tata 1mg"]),
    "Travel": (3500, 0.8, 1, ["IRCTC", "MakeMyTrip", "RedBus", "IndiGo"]),
    "Personal Care": (600, 0.5, 1.5, ["Urban Company", "Salon", "Nykaa"]),
    "Other": (1000, 0.8, 3, ["ATM Withdrawal", "Transfer to Friend", "Mutual Fund SIP"]),
}

MONTHS = pd.date_range("2025-11-01", "2026-10-01", freq="MS")


def make_user_rows(user_id):
    scale = rng.lognormal(0, 0.3)  # each user spends a bit differently
    rent = int(rng.choice(range(8000, 30001, 1000)))
    rows = []
    for month in MONTHS:
        days = calendar.monthrange(month.year, month.month)[1]

        # fixed monthly rent
        rows.append((user_id, month.replace(day=int(rng.integers(1, 6))), 10,
                     "House Rent", "Rent", float(rent)))

        for cat, (median, spread, freq, merchants) in PROFILE.items():
            for _ in range(rng.poisson(freq)):
                day = int(rng.integers(1, days + 1))
                hour = int(np.clip(rng.normal(15, 4), 7, 23))
                amount = max(20.0, round(median * scale * rng.lognormal(0, spread)))
                rows.append((user_id, month.replace(day=day), hour,
                             str(rng.choice(merchants)), cat, float(amount)))
    return rows


def build():
    rows = []
    for u in range(1, N_USERS + 1):
        rows.extend(make_user_rows(f"U{u:02d}"))

    df = pd.DataFrame(rows, columns=["user_id", "date", "hour", "description", "category", "amount"])
    df["is_anomaly"] = 0
    df["anomaly_type"] = "none"

    # ---- inject anomalies (never into Rent) ----
    candidates = df.index[df["category"] != "Rent"].to_numpy()
    n_anom = int(len(df) * ANOMALY_RATE)
    chosen = rng.choice(candidates, size=n_anom, replace=False)
    n_spike, n_odd = int(n_anom * 0.5), int(n_anom * 0.25)
    spike_idx, odd_idx, dup_idx = chosen[:n_spike], chosen[n_spike:n_spike + n_odd], chosen[n_spike + n_odd:]

    # 1) spike: amount way above this user's norm
    df.loc[spike_idx, "amount"] = (df.loc[spike_idx, "amount"] * rng.uniform(6, 15, len(spike_idx))).round()
    df.loc[spike_idx, ["is_anomaly", "anomaly_type"]] = [1, "spike"]

    # 2) odd hour: bigger-than-usual payment in the middle of the night
    df.loc[odd_idx, "hour"] = rng.integers(1, 5, len(odd_idx))
    df.loc[odd_idx, "amount"] = (df.loc[odd_idx, "amount"] * rng.uniform(3, 6, len(odd_idx))).round()
    df.loc[odd_idx, ["is_anomaly", "anomaly_type"]] = [1, "odd_hour"]

    # 3) duplicate: the same payment charged again on the same day
    dups = df.loc[dup_idx].copy()
    dups["is_anomaly"] = 1
    dups["anomaly_type"] = "duplicate"
    df = pd.concat([df, dups], ignore_index=True)

    return df.sort_values(["user_id", "date", "hour"]).reset_index(drop=True)


if __name__ == "__main__":
    df = build()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "transactions.csv")
    df.to_csv(out, index=False)
    print(f"Saved {len(df)} rows to {out}")
    print("\nAnomalies:", int(df["is_anomaly"].sum()), f"({df['is_anomaly'].mean():.1%})")
    print(df["anomaly_type"].value_counts())
    print(df.head(8))