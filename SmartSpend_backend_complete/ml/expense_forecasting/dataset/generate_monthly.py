"""
Generates 36 months of synthetic monthly spending for forecasting.
Output: monthly_spending.csv in the same folder as this script.
Columns: user_id, month, category, amount

Built-in patterns (the model must discover these on its own):
  - gradual growth in spending over time (inflation / lifestyle creep)
  - seasonality (festival shopping, summer electricity, holiday travel, ...)
  - yearly rent increases
  - occasional one-off spikes (a wedding, a medical bill, a big trip)

Run from the SmartSpend root:
    python ml/expense_forecasting/dataset/generate_monthly.py
"""
import os

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

N_USERS = 30
MONTHS = pd.date_range("2023-11-01", "2026-10-01", freq="MS")  # 36 months

# category: (typical monthly spend in INR, month-to-month noise)
PROFILE = {
    "Food": (4900, 0.12),
    "Groceries": (7200, 0.10),
    "Transport": (3000, 0.15),
    "Shopping": (6000, 0.35),
    "Bills & Utilities": (2400, 0.10),
    "Entertainment": (1200, 0.25),
    "Health": (1400, 0.40),
    "Travel": (3500, 0.60),
    "Personal Care": (900, 0.25),
    "Other": (3000, 0.40),
}

# calendar month -> multiplier (months not listed are 1.0)
SEASON = {
    "Food": {10: 1.10, 12: 1.15},
    "Shopping": {1: 1.15, 10: 1.40, 11: 1.30, 12: 1.20},
    "Travel": {5: 1.50, 6: 1.40, 10: 1.30, 12: 1.60},
    "Bills & Utilities": {1: 0.90, 2: 0.90, 4: 1.25, 5: 1.35, 6: 1.30, 12: 0.90},
    "Entertainment": {6: 1.20, 12: 1.25},
    "Health": {7: 1.20, 8: 1.20, 9: 1.15},
}

ONE_OFF_CATEGORIES = {"Travel", "Shopping", "Health", "Other"}
ONE_OFF_PROB = 0.04


def build():
    rows = []
    for u in range(1, N_USERS + 1):
        user = f"U{u:02d}"
        scale = rng.lognormal(0, 0.3)                      # some users spend more than others
        growth = max(0.0, rng.normal(0.005, 0.003))        # monthly growth rate
        rent = float(rng.choice(range(8000, 30001, 1000)))
        hike_month = int(rng.integers(1, 13))              # month the rent goes up each year

        for t, month in enumerate(MONTHS):
            if t > 0 and month.month == hike_month:
                rent = round(rent * (1 + rng.uniform(0.05, 0.08)), -2)
            rows.append((user, month, "Rent", rent))

            for cat, (base, noise) in PROFILE.items():
                amount = base * scale * (1 + growth) ** t
                amount *= SEASON.get(cat, {}).get(month.month, 1.0)
                amount *= rng.lognormal(0, noise)
                if cat in ONE_OFF_CATEGORIES and rng.random() < ONE_OFF_PROB:
                    amount *= rng.uniform(2, 4)
                rows.append((user, month, cat, round(amount)))

    df = pd.DataFrame(rows, columns=["user_id", "month", "category", "amount"])
    return df.sort_values(["user_id", "month", "category"]).reset_index(drop=True)


if __name__ == "__main__":
    df = build()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "monthly_spending.csv")
    df.to_csv(out, index=False)
    print(f"Saved {len(df)} rows to {out}")
    print("Users:", df["user_id"].nunique(), "| Months:", df["month"].nunique(),
          "| Categories:", df["category"].nunique())
    print("Date range:", df["month"].min().date(), "to", df["month"].max().date())
    totals = df.groupby(["user_id", "month"])["amount"].sum().groupby("month").mean().round(0)
    print("\nAverage total monthly spend per user (first 6 and last 6 months):")
    print(pd.concat([totals.head(6), totals.tail(6)]))
    print(df.head(8))