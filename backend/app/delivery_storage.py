import csv
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from backend.app import csv_storage

ORDER_HEADERS = [
    "id",
    "customer_id",
    "current_status",
    "restaurant_id",
    "food_item",
    "order_value",
    "created_at",
    "updated_at",
]

STATUS_HEADERS = [
    "id",
    "order_id",
    "status",
    "updated_at",
    "updated_by_role",
]


@dataclass(frozen=True)
class OrderRecord:
    id: int
    customer_id: str
    current_status: str
    restaurant_id = None
    food_item = None
    order_value = None
    created_at = None
    updated_at = None


@dataclass(frozen=True)
class StatusHistoryEntry:
    status: str
    updated_at: datetime
    updated_by_role: str | None = None


def _orders_path():
    return Path(os.environ.get("DELIVERY_ORDERS_CSV_PATH", "data/delivery_orders.csv"))


def _status_path():
    return Path(
        os.environ.get(
            "DELIVERY_STATUS_UPDATES_CSV_PATH",
            "data/delivery_status_updates.csv",
        )
    )


def _parse_dt(value):
    if not value:
        return None
    v = value.strip()
    if v.endswith("Z"):
        v = v[:-1] + "+00:00"
    return datetime.fromisoformat(v)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def ensure_delivery_csv_files():
    op = csv_storage.ensure_csv_file(_orders_path(), ORDER_HEADERS)
    sp = csv_storage.ensure_csv_file(_status_path(), STATUS_HEADERS)
    return op, sp


def row_to_order(row):
    rid = row["restaurant_id"].strip()
    ov = row["order_value"].strip()
    return OrderRecord(
        id=int(row["id"]),
        customer_id=row["customer_id"],
        current_status=row["current_status"],
        restaurant_id=int(rid) if rid else None,
        food_item=row["food_item"] or None,
        order_value=float(ov) if ov else None,
        created_at=_parse_dt(row.get("created_at", "")),
        updated_at=_parse_dt(row.get("updated_at", "")),
    )


def order_to_row(order):
    return {
        "id": str(order.id),
        "customer_id": order.customer_id,
        "current_status": order.current_status,
        "restaurant_id": str(order.restaurant_id) if order.restaurant_id is not None else "",
        "food_item": order.food_item or "",
        "order_value": str(order.order_value) if order.order_value is not None else "",
        "created_at": order.created_at.isoformat() if order.created_at else "",
        "updated_at": order.updated_at.isoformat() if order.updated_at else "",
    }


def load_orders():
    path, _ = ensure_delivery_csv_files()
    return [row_to_order(r) for r in csv_storage.read_rows(path, ORDER_HEADERS)]


def save_orders(orders):
    path, _ = ensure_delivery_csv_files()
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ORDER_HEADERS)
        w.writeheader()
        for o in orders:
            w.writerow(order_to_row(o))


def find_order_by_id(order_id):
    for o in load_orders():
        if o.id == order_id:
            return o
    return None


def append_status(
    order_id,
    status,
    updated_by_role,
):
    _, sp = ensure_delivery_csv_files()
    rows = csv_storage.read_rows(sp, STATUS_HEADERS)
    new_id = csv_storage.next_int_id(rows, "id")
    csv_storage.append_row(
        sp,
        STATUS_HEADERS,
        {
            "id": str(new_id),
            "order_id": str(order_id),
            "status": status,
            "updated_at": _now_iso(),
            "updated_by_role": updated_by_role or "",
        },
    )


def load_status_history(order_id):
    _, sp = ensure_delivery_csv_files()
    rows = csv_storage.read_rows(sp, STATUS_HEADERS)
    entries = []
    for row in rows:
        if int(row["order_id"]) != order_id:
            continue
        role = (row.get("updated_by_role") or "").strip() or None
        entries.append(
            StatusHistoryEntry(
                status=row["status"],
                updated_at=_parse_dt(row["updated_at"]) or datetime.now(timezone.utc),
                updated_by_role=role,
            )
        )
    entries.sort(key=lambda e: e.updated_at)
    return entries
