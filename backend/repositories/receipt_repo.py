import csv
import os
from datetime import datetime
from pathlib import Path

from backend.app import csv_storage

RECEIPT_HEADERS = [
    "id", "payment_id", "order_id", "customer_id", "receipt_number",
    "amount", "tax", "total", "payment_method", "issued_at",
]


def get_csv_path():
    return Path(os.environ.get("RECEIPTS_CSV_PATH", "data/receipts.csv"))


def _row_to_dict(row):
    return {
        "id": int(row["id"]),
        "payment_id": int(row["payment_id"]),
        "order_id": int(row["order_id"]),
        "customer_id": row["customer_id"],
        "receipt_number": row["receipt_number"],
        "amount": float(row["amount"]),
        "tax": float(row["tax"]),
        "total": float(row["total"]),
        "payment_method": row["payment_method"],
        "issued_at": row["issued_at"],
    }


def _dict_to_row(d):
    return {k: str(v) for k, v in d.items()}


def _load_all():
    path = get_csv_path()
    csv_storage.ensure_csv_file(path, RECEIPT_HEADERS)
    return [_row_to_dict(r) for r in csv_storage.read_rows(path, RECEIPT_HEADERS)]


def create_receipt(data):
    path = get_csv_path()
    rows = csv_storage.read_rows(path, RECEIPT_HEADERS)
    data["id"] = csv_storage.next_int_id(rows)
    data["issued_at"] = datetime.now().isoformat()
    csv_storage.append_row(path, RECEIPT_HEADERS, _dict_to_row(data))
    return data


def get_receipt_by_order_id(order_id):
    for r in _load_all():
        if r["order_id"] == order_id:
            return r
    return None


def clear():
    path = get_csv_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RECEIPT_HEADERS)
        writer.writeheader()
