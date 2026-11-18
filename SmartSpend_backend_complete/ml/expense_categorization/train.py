"""Trains the expense categorization model and saves it to models/.

Run from the SmartSpend root:
    python ml/expense_categorization/train.py
"""
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

try:  # imported as part of the ml package (e.g. by the backend)
    from .text_utils import clean_text
except ImportError:  # run directly as a script
    from text_utils import clean_text

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "dataset" / "expenses.csv"
MODEL_PATH = BASE_DIR / "models" / "expense_classifier.joblib"


def main():
    df = pd.read_csv(DATA_PATH)
    df["clean"] = df["description"].apply(clean_text)

    X_train, X_test, y_train, y_test = train_test_split(
        df["clean"], df["category"],
        test_size=0.2, random_state=42, stratify=df["category"],
    )

    model = Pipeline([
        ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5))),
        ("clf", LogisticRegression(C=10, max_iter=2000)),
    ])
    model.fit(X_train, y_train)

    print(f"Test accuracy: {model.score(X_test, y_test):.4f}")
    print(classification_report(y_test, model.predict(X_test)))

    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()
