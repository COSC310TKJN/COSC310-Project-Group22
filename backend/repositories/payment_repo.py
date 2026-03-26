import csv
import os
from datetime import datetime
from pathlib import Path

from backend.app import csv_storage

PAYMENT_HEADERS = [
    "id", "order_id", "customer_id", "amount", "payment_method",
    "status", "transaction_id", "created_at", "updated_at",
]


def get_csv_path():
    return Path(os.environ.get("PAYMENTS_CSV_PATH", "data/payments.csv"))


def _row_to_dict(row):
    return {
        "id": int(row["id"]),
        "order_id": int(row["order_id"]),
        "customer_id": row["customer_id"],
        "amount": float(row["amount"]),
        "payment_method": row["payment_method"],
        "status": row["status"],
        "transaction_id": row["transaction_id"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _dict_to_row(d):
    return {k: str(v) for k, v in d.items()}


def _load_all():
    path = get_csv_path()
    csv_storage.ensure_csv_file(path, PAYMENT_HEADERS)
    return [_row_to_dict(r) for r in csv_storage.read_rows(path, PAYMENT_HEADERS)]


def create_payment(data):
    path = get_csv_path()
    rows = csv_storage.read_rows(path, PAYMENT_HEADERS)
    data["id"] = csv_storage.next_int_id(rows)
    data["created_at"] = datetime.now().isoformat()
    data["updated_at"] = datetime.now().isoformat()
    csv_storage.append_row(path, PAYMENT_HEADERS, _dict_to_row(data))
    return data


def get_payment_by_id(payment_id):
    for p in _load_all():
        if p["id"] == payment_id:
            return p
    return None


def get_payment_by_order_id(order_id):
    for p in _load_all():
        if p["order_id"] == order_id:
            return p
    return None


def get_payments_by_status(status):
    return [p for p in _load_all() if p["status"] == status]


def clear():
    path = get_csv_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PAYMENT_HEADERS)
        writer.writeheader()
