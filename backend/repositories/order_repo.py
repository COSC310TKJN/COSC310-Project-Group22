import os
import csv
from pathlib import Path
from backend.models.order import Order, OrderStatus

ORDER_HEADERS = [
    "order_id",
    "restaurant_id",
    "food_item",
    "order_time",
    "order_value",
    "delivery_method",
    "delivery_distance",
    "customer_id",
    "source_order_id",
    "traffic_condition",
    "weather_condition",
    "route_taken",
    "coupon_code",
    "status"
]


def get_orders_csv_path() -> Path:
    return Path(os.environ.get("ORDERS_CSV_PATH", "data/orders.csv"))


def ensure_orders_csv_exists() -> Path:
    path = get_orders_csv_path()
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(ORDER_HEADERS)
    return path


def row_to_order(row: dict) -> Order:
    order = Order(
        order_id=row["order_id"],
        restaurant_id=int(row["restaurant_id"]),
        food_item=row["food_item"],
        order_time=row["order_time"],
        order_value=float(row["order_value"]),
        delivery_method=row["delivery_method"],
        delivery_distance=float(row["delivery_distance"]),
        customer_id=row["customer_id"],
        source_order_id=row.get("source_order_id") or None,
        traffic_condition=row["traffic_condition"] or None,
        weather_condition=row["weather_condition"] or None,
        route_taken=row["route_taken"] or None,
        coupon_code=row.get("coupon_code") or None
    )

    order.status = OrderStatus(row["status"])
    return order


def order_to_row(order: Order) -> dict:
    return {
        "order_id": order.order_id,
        "restaurant_id": str(order.restaurant_id),
        "food_item": order.food_item,
        "order_time": order.order_time,
        "order_value": str(order.order_value),
        "delivery_method": order.delivery_method,
        "delivery_distance": str(order.delivery_distance),
        "customer_id": order.customer_id,
        "source_order_id": order.source_order_id or "",
        "traffic_condition": order.traffic_condition or "",
        "weather_condition": order.weather_condition or "",
        "route_taken": order.route_taken or "",
        "coupon_code": order.coupon_code or "",
        "status": order.status.value
    }


def read_rows() -> list:
    path = ensure_orders_csv_exists()
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_rows(rows: list) -> None:
    path = ensure_orders_csv_exists()
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ORDER_HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def load_orders() -> dict:
    orders = {}
    for row in read_rows():
        order = row_to_order(row)
        orders[order.order_id] = order
    return orders


orders_db = load_orders()


class OrderRepository:

    @staticmethod
    def save(order: Order):
        orders_db[order.order_id] = order
        rows = [order_to_row(o) for o in orders_db.values()]
        write_rows(rows)
        return order

    @staticmethod
    def find_by_id(order_id: str):
        return orders_db.get(order_id)

    @staticmethod
    def find_all():
        return list(orders_db.values())

    @staticmethod
    def delete(order_id: str):
        if order_id in orders_db:
            del orders_db[order_id]
            rows = [order_to_row(o) for o in orders_db.values()]
            write_rows(rows)
            return True
        return False

    @staticmethod
    def exists(order_id: str):
        return order_id in orders_db
