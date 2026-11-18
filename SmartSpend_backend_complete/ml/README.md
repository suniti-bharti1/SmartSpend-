# SmartSpend ML

Three independent models. Each lives in its own folder with a `train.py` (builds the model) and a `predict.py` (the functions the app calls).

| Folder | What it does | Main function |
|---|---|---|
| `expense_categorization/` | Assigns a category to a transaction description | `predict_category(description)` |
| `anomaly_detection/` | Flags unusual transactions (spikes, odd hours, duplicates) | `check_transaction(txn, history)` |
| `expense_forecasting/` | Forecasts next month's spend per category, with a range | `forecast_next_month(history)` |

> **All three were trained on synthetic data** (Indian merchants, simulated users). Treat the results as a working baseline, not final accuracy. Retrain on real transactions when available.

## 1. Setup

Run everything from the **SmartSpend root folder** with the virtual environment active.

```
venv\Scripts\activate
pip install pandas numpy scikit-learn joblib
```

Trained models (`*.joblib`) and generated CSVs are not stored in git. After cloning, rebuild them once:

```
python ml\expense_categorization\dataset\generate_dataset.py
python ml\expense_categorization\train.py
python ml\anomaly_detection\dataset\generate_transactions.py
python ml\anomaly_detection\train.py
python ml\expense_forecasting\dataset\generate_monthly.py
python ml\expense_forecasting\train.py
```

Each `train.py` prints its accuracy and saves the model into that folder's `models/` directory. Each `predict.py` can also be run directly for a quick demo.

## 2. Using the models from Python

From the SmartSpend root, all three can be imported together:

```python
from ml.expense_categorization.predict import predict_category
from ml.anomaly_detection.predict import check_transaction, detect_anomalies
from ml.expense_forecasting.predict import forecast_next_month, forecast_totals
```

### Expense categorization

```python
predict_category("Swiggy order 450")
# {'category': 'Food', 'confidence': 0.77, 'needs_review': False}
```

- Input: any transaction description (UPI prefixes, numbers and casing are handled).
- `confidence` is 0 to 1. `needs_review` is `True` when confidence is below 0.5, so the app should ask the user to confirm instead of auto-assigning.
- Categories: Food, Groceries, Transport, Shopping, Bills & Utilities, Entertainment, Health, Rent, Travel, Personal Care, Other.
- Words the model has never seen (for example "Dentist appointment") come back with low confidence and `needs_review = True`. That is intended.

### Anomaly detection

```python
check_transaction(
    {"user_id": "U01", "date": "2026-11-05", "hour": 3,
     "description": "Amazon", "category": "Shopping", "amount": 4000},
    user_history_dataframe,
)
# {'is_anomaly': True, 'reason': 'unusual time of day', 'typical_amount': 1676, 'score': 0.094}
```

- `txn` needs: `user_id`, `date` (YYYY-MM-DD), `hour` (0 to 23), `description`, `category`, `amount`.
- `user_history_dataframe` holds that user's past transactions with the same columns. A user's "usual" amount comes from this history; with fewer than 5 past payments in a category it falls back to the all-user average.
- `reason` is plain English and safe to show in the UI. `score` is higher for stranger transactions.
- `detect_anomalies(df)` does the same for a whole DataFrame at once.
- Use the category from `predict_category` as the `category` input.

### Expense forecasting

```python
forecast_next_month(monthly_history_dataframe)
# DataFrame: user_id, category, month, low, expected, high, method
forecast_totals(forecast)   # expected total per user
```

- Input columns: `user_id`, `month`, `category`, `amount` (amount = total spent in that month). Build it from transactions like this:

```python
monthly = (tx.assign(month=pd.to_datetime(tx["date"]).dt.to_period("M").dt.to_timestamp())
             .groupby(["user_id", "month", "category"], as_index=False)["amount"].sum())
```

- The forecast is for the month after each user's latest month. Works for one user or many.
- `method = "model"` (12 or more months of history) or `"fallback"` (3 to 11 months: recent median, range from recent min to max). Fewer than 3 months returns no forecast for that category.
- Show `low` to `high` as a "likely range". It contains the real value about 3 times out of 4, so do not describe it as a guarantee.
- For the total, use `forecast_totals`. Do not add up all the `low` and `high` values (that range would be far too wide).

## 3. Not a Python backend?

These are Python functions. A Node, Java or Salesforce backend needs a small HTTP wrapper around them (for example FastAPI with one endpoint per function). That wrapper is not included yet.

## 4. Known limits

- Synthetic training data: expect lower accuracy on real transactions until retrained.
- Anomaly detection catches about 85% of the injected anomalies at about 67% precision, so present flags as "worth a look", not as confirmed fraud.
- Forecasts are best for steady categories (Rent, Groceries, Food, Bills) and weakest for spiky ones (Travel, Shopping, Health). Ranges reflect that.
- Models are saved with the scikit-learn version used to train them. Load them with the same version (see each folder's `requirements.txt`).
