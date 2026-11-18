"""Loads the trained model and predicts the category of an expense.

Use from other code:
    from predict import predict_category
    predict_category("Swiggy order 450")

Or test from the terminal:
    python ml/expense_categorization/predict.py "Swiggy order 450"
"""
import sys
from pathlib import Path

import joblib

try:  # imported as part of the ml package (e.g. by the backend)
    from .text_utils import clean_text
except ImportError:  # run directly as a script
    from text_utils import clean_text

MODEL_PATH = Path(__file__).resolve().parent / "models" / "expense_classifier.joblib"
REVIEW_THRESHOLD = 0.50  # below this confidence, flag the result for review

_model = None


def _load_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"No trained model at {MODEL_PATH}. Run train.py first.")
        _model = joblib.load(MODEL_PATH)
    return _model


def predict_category(description):
    """Returns {'category': str, 'confidence': float, 'needs_review': bool}."""
    model = _load_model()
    probs = model.predict_proba([clean_text(description)])[0]
    best = probs.argmax()
    confidence = float(probs[best])
    return {
        "category": str(model.classes_[best]),
        "confidence": round(confidence, 3),
        "needs_review": confidence < REVIEW_THRESHOLD,
    }


if __name__ == "__main__":
    text = " ".join(sys.argv[1:]) or "Swiggy order 450"
    print(predict_category(text))
