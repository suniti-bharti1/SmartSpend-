"""Trains the anomaly detector and saves it to models/.

Run from the SmartSpend root:
    python ml/anomaly_detection/train.py
"""
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, confusion_matrix

try:  # imported as part of the ml package (e.g. by the backend)
    from .features import ML_FEATURES, add_features
except ImportError:  # run directly as a script
    from features import ML_FEATURES, add_features

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "dataset" / "transactions.csv"
MODEL_PATH = BASE_DIR / "models" / "anomaly_detector.joblib"

CONTAMINATION = 0.015  # share of transactions the ML layer flags; tune for fewer/more alerts


def main():
    df = pd.read_csv(DATA_PATH)
    global_medians = df.groupby("category")["amount"].median().to_dict()

    feat = add_features(df, global_medians)
    model = IsolationForest(n_estimators=200, contamination=CONTAMINATION, random_state=42)
    model.fit(feat[ML_FEATURES])

    # Grade against the hidden labels (only possible because the data is synthetic)
    flag_ml = model.predict(feat[ML_FEATURES]) == -1
    flag_hybrid = (flag_ml | (feat["is_repeat"] == 1)).astype(int)
    print(classification_report(feat["is_anomaly"], flag_hybrid, digits=3))
    print(confusion_matrix(feat["is_anomaly"], flag_hybrid))
    print(feat.assign(flag=flag_hybrid).query("is_anomaly == 1")
          .groupby("anomaly_type")["flag"].mean().round(2).to_string())

    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump({"model": model, "global_medians": global_medians}, MODEL_PATH)
    print(f"\nModel saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()
