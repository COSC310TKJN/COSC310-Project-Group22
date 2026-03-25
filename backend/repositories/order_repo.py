import json
import os
from backend.models.order import Order, OrderStatus


DATA_FILE = os.path.join(os.path.dirname(__file__), "../../data/order.json")


def load_orders():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        orders = {}
        for order_id, order_data in data.items():
            order = Order(
                order_id=order_data["order_id"],
                restaurant_id=order_data["restaurant_id"],
                food_item=order_data["food_item"],
                order_time=order_data["order_time"],
                order_value=order_data["order_value"],
                delivery_method=order_data["delivery_method"],
                delivery_distance=order_data["delivery_distance"],
                customer_id=order_data["customer_id"],
                traffic_condition=order_data.get("traffic_condition"),
                weather_condition=order_data.get("weather_condition"),
                route_taken=order_data.get("route_taken")
            )
            order.status = OrderStatus(order_data["status"])
            orders[order_id] = order
            
        return orders


def save_orders(orders):
    data = {}
    for order_id, order in orders.items():
        data[order_id] = order.to_dict()
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


orders_db = load_orders()


class OrderRepository:

    @staticmethod
    def save(order: Order):
        orders_db[order.order_id] = order
        save_orders(orders_db)
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
            save_orders(orders_db)
            return True
        return False

    @staticmethod
    def exists(order_id: str):
        return order_id in orders_db