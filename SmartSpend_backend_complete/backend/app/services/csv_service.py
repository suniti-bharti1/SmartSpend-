import csv, io
from datetime import datetime
from fastapi import HTTPException

def parse_transactions(raw: bytes) -> list[dict]:
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(400, "CSV must be UTF-8 encoded. Save/export it as CSV UTF-8.")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise HTTPException(400, "CSV is empty or has no header row.")
    headers = {h.strip().lower(): h for h in reader.fieldnames if h}
    date_col = headers.get("date") or headers.get("transaction date")
    desc_col = headers.get("description") or headers.get("narration") or headers.get("merchant") or headers.get("details")
    amount_col = headers.get("amount")
    debit_col = headers.get("debit") or headers.get("withdrawal")
    credit_col = headers.get("credit") or headers.get("deposit")
    type_col = headers.get("transaction_type") or headers.get("type")
    if not date_col or not desc_col or not (amount_col or debit_col or credit_col):
        raise HTTPException(400, "Required columns: date, description, amount. Alternatively use debit and/or credit columns.")
    result=[]
    for line, row in enumerate(reader, start=2):
        try:
            d = datetime.fromisoformat(str(row[date_col]).strip().replace("Z", "+00:00")).date()
            desc = str(row[desc_col] or "").strip()
            if not desc: raise ValueError("empty description")
            if amount_col:
                amount = abs(float(str(row[amount_col]).replace(",", "").replace("₹", "").strip()))
                kind = (str(row.get(type_col, "") or "").strip().lower() if type_col else "")
                if kind not in ("income", "expense"):
                    raw_amount = float(str(row[amount_col]).replace(",", "").replace("₹", "").strip())
                    kind = "income" if raw_amount < 0 else "expense"
            else:
                debit = abs(float(str(row.get(debit_col, "0") or "0").replace(",", "").replace("₹", "").strip())) if debit_col else 0
                credit = abs(float(str(row.get(credit_col, "0") or "0").replace(",", "").replace("₹", "").strip())) if credit_col else 0
                if debit and credit: raise ValueError("both debit and credit are filled")
                amount, kind = (credit, "income") if credit else (debit, "expense")
            if amount <= 0: continue
            result.append({"date": d, "hour": 12, "description": desc, "amount": amount, "transaction_type": kind})
        except Exception as exc:
            raise HTTPException(400, f"Invalid CSV row {line}: {exc}")
    if not result:
        raise HTTPException(400, "No valid transactions found in CSV.")
    if len(result) > 10000:
        raise HTTPException(400, "Maximum 10,000 transactions per upload.")
    return result
