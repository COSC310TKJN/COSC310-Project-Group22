import csv
import os
from datetime import datetime
from pathlib import Path

from backend.app import csv_storage

REVIEW_HEADERS = [
    "id", "customer_id", "order_id", "restaurant_id",
    "rating", "comment", "created_at",
]


def get_csv_path() -> Path:
    return Path(os.environ.get("REVIEWS_CSV_PATH", "data/reviews.csv"))


def _row_to_dict(row: dict[str, str]) -> dict:
    comment = row["comment"]
    return {
        "id": int(row["id"]),
        "customer_id": row["customer_id"],
        "order_id": int(row["order_id"]),
        "restaurant_id": int(row["restaurant_id"]),
        "rating": int(row["rating"]),
        "comment": comment if comment else None,
        "created_at": row["created_at"],
    }


def _dict_to_row(d: dict) -> dict[str, str]:
    return {
        "id": str(d["id"]),
        "customer_id": d["customer_id"],
        "order_id": str(d["order_id"]),
        "restaurant_id": str(d["restaurant_id"]),
        "rating": str(d["rating"]),
        "comment": d["comment"] if d["comment"] is not None else "",
        "created_at": d["created_at"],
    }


def _load_all() -> list[dict]:
    path = get_csv_path()
    csv_storage.ensure_csv_file(path, REVIEW_HEADERS)
    return [_row_to_dict(r) for r in csv_storage.read_rows(path, REVIEW_HEADERS)]


def create_review(data: dict) -> dict:
    path = get_csv_path()
    rows = csv_storage.read_rows(path, REVIEW_HEADERS)
    data["id"] = csv_storage.next_int_id(rows)
    data["created_at"] = datetime.now().isoformat()
    csv_storage.append_row(path, REVIEW_HEADERS, _dict_to_row(data))
    return data


def get_review_by_id(review_id: int) -> dict | None:
    for r in _load_all():
        if r["id"] == review_id:
            return r
    return None


def get_review_by_order(order_id: int, customer_id: str) -> dict | None:
    for r in _load_all():
        if r["order_id"] == order_id and r["customer_id"] == customer_id:
            return r
    return None


def get_reviews_by_restaurant(restaurant_id: int) -> list[dict]:
    return [r for r in _load_all() if r["restaurant_id"] == restaurant_id]


def get_reviews_by_customer(customer_id: str) -> list[dict]:
    results = [r for r in _load_all() if r["customer_id"] == customer_id]
    return sorted(results, key=lambda x: x["created_at"], reverse=True)


def clear() -> None:
    path = get_csv_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REVIEW_HEADERS)
        writer.writeheader()
