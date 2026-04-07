import uuid

from backend.models.order import Order, OrderStatus
from backend.repositories.order_repo import OrderRepository, orders_db
from backend.services.pricing_service import PricingService

reorder_drafts = {}


class OrderService:

    @staticmethod
    def create_order(order_data):
        order = Order(
            order_id=order_data.order_id,
            restaurant_id=order_data.restaurant_id,
            food_item=order_data.food_item,
            order_time=order_data.order_time,
            order_value=order_data.order_value,
            delivery_method=order_data.delivery_method,
            delivery_distance=order_data.delivery_distance,
            customer_id=order_data.customer_id,
            source_order_id=getattr(order_data, "source_order_id", None),
            traffic_condition=order_data.traffic_condition,
            weather_condition=order_data.weather_condition,
            route_taken=order_data.route_taken,
        )
        return OrderRepository.save(order)

    @staticmethod
    def get_order(order_id):
        return OrderRepository.find_by_id(order_id)

    @staticmethod
    def cancel_order(order_id):
        order = OrderRepository.find_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        order.cancel()
        return OrderRepository.save(order)

    @staticmethod
    def calculate_order_total(order_id):
        order = OrderRepository.find_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        return PricingService.calc_total(order)

    @staticmethod
    def update_order(order_id, updates):
        order = OrderRepository.find_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        if order.status == OrderStatus.COMPLETED:
            raise ValueError("Cannot modify a completed order")
        for key, value in updates.items():
            setattr(order, key, value)
        return OrderRepository.save(order)

    @staticmethod
    def get_order_history(customer_id):
        customer_orders = [
            order for order in OrderRepository.find_all() if order.customer_id == customer_id
        ]
        return sorted(customer_orders, key=lambda order: str(order.order_time), reverse=True)

    @staticmethod
    def next_order_id():
        max_numeric_id = 0
        for order in OrderRepository.find_all():
            try:
                max_numeric_id = max(max_numeric_id, int(order.order_id))
            except ValueError:
                continue
        return str(max_numeric_id + 1)

    @staticmethod
    def create_reorder_draft(source_order_id, customer_id):
        source_order = OrderRepository.find_by_id(source_order_id)
        if not source_order:
            raise LookupError("Order not found")
        if source_order.customer_id != customer_id:
            raise PermissionError("Cannot reorder another customer's order")
        source_status = (
            source_order.status.value
            if isinstance(source_order.status, OrderStatus)
            else str(source_order.status)
        )
        if source_status != OrderStatus.DELIVERED.value:
            raise ValueError("Only delivered orders can be reordered")

        draft_id = uuid.uuid4().hex
        reorder_drafts[draft_id] = {
            "source_order_id": source_order.order_id,
            "customer_id": customer_id,
            "order_payload": {
                "restaurant_id": source_order.restaurant_id,
                "food_item": source_order.food_item,
                "order_time": source_order.order_time,
                "order_value": source_order.order_value,
                "delivery_method": source_order.delivery_method,
                "delivery_distance": source_order.delivery_distance,
                "customer_id": source_order.customer_id,
                "traffic_condition": source_order.traffic_condition,
                "weather_condition": source_order.weather_condition,
                "route_taken": source_order.route_taken,
                "source_order_id": source_order.order_id,
            },
        }
        return draft_id, reorder_drafts[draft_id]["order_payload"]

    @staticmethod
    def update_reorder_draft(draft_id, updates):
        draft = reorder_drafts.get(draft_id)
        if not draft:
            raise LookupError("Reorder draft not found")

        allowed_fields = {"order_time", "delivery_method", "delivery_distance"}
        invalid_fields = set(updates.keys()) - allowed_fields
        if invalid_fields:
            raise ValueError(
                "Only order_time, delivery_method, and delivery_distance can be edited"
            )
        if not updates:
            raise ValueError("At least one editable field must be provided")

        draft["order_payload"].update(updates)
        return draft["order_payload"]

    @staticmethod
    def confirm_reorder(draft_id):
        draft = reorder_drafts.get(draft_id)
        if not draft:
            raise LookupError("Reorder draft not found")

        payload = dict(draft["order_payload"])
        payload["order_id"] = OrderService.next_order_id()
        order = Order(
            order_id=payload["order_id"],
            restaurant_id=payload["restaurant_id"],
            food_item=payload["food_item"],
            order_time=payload["order_time"],
            order_value=payload["order_value"],
            delivery_method=payload["delivery_method"],
            delivery_distance=payload["delivery_distance"],
            customer_id=payload["customer_id"],
            source_order_id=payload.get("source_order_id"),
            traffic_condition=payload.get("traffic_condition"),
            weather_condition=payload.get("weather_condition"),
            route_taken=payload.get("route_taken"),
        )
        saved_order = OrderRepository.save(order)
        del reorder_drafts[draft_id]
        return saved_order
