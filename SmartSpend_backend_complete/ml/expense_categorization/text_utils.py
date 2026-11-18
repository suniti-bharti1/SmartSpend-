"""Shared text cleaning used by both train.py and predict.py."""
import re

NOISE_WORDS = {"upi", "dr", "pos", "paytm", "phonepe", "gpay", "neft", "imps", "ref", "txn"}


def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"@\w+", " ", text)       # bank handles like @ybl
    text = re.sub(r"[^a-z\s]", " ", text)   # numbers and symbols
    words = [w for w in text.split() if w not in NOISE_WORDS]
    return " ".join(words)