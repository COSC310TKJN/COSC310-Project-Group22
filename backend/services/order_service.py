import uuid

from backend.app.config import settings
from backend.models.order import Order, OrderStatus
from backend.repositories.order_repo import OrderRepository, orders_db
from backend.services.pricing_service import PricingService
from backend.services.coupon_service import CouponService

reorder_drafts = {}


class OrderService:

    @staticmethod
    def create_order(order_data):
        fixed_km = float(settings.FIXED_DELIVERY_DISTANCE_KM)
        order = Order(
            order_id=order_data.order_id,
            restaurant_id=order_data.restaurant_id,
            food_item=order_data.food_item,
            order_time=order_data.order_time,
            order_value=order_data.order_value,
            delivery_method=order_data.delivery_method,
            delivery_distance=fixed_km,
            customer_id=order_data.customer_id,
            source_order_id=getattr(order_data, "source_order_id", None),
            traffic_condition=order_data.traffic_condition,
            weather_condition=order_data.weather_condition,
            route_taken=order_data.route_taken,
            coupon_code=OrderService._normalize_coupon_code(
                getattr(order_data, "coupon_code", None)
            ),
        )
        return OrderRepository.save(order)

    @staticmethod
    def _normalize_coupon_code(raw):
        if raw is None:
            return None
        s = str(raw).strip()
        return s.upper() if s else None

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

        pricing = dict(PricingService.calc_total(order))
        pre_coupon_total = pricing["total"]
        code = (order.coupon_code or "").strip().upper()
        pricing["discount"] = 0.0
        pricing["coupon_applied"] = False
        pricing["coupon_error"] = None

        if code:
            pricing["coupon_code"] = code
            try:
                final_total = CouponService.apply_coupon(code, pre_coupon_total)
                pricing["discount"] = round(pre_coupon_total - final_total, 2)
                pricing["total"] = round(final_total, 2)
                pricing["coupon_applied"] = True
            except ValueError as error:
                pricing["coupon_error"] = str(error)
                pricing["coupon_applied"] = False
        return pricing

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
    def list_all_orders():
        return sorted(
            OrderRepository.find_all(),
            key=lambda o: str(o.order_time),
            reverse=True,
        )

    @staticmethod
    def admin_update_order(order_id: str, updates: dict):
        order = OrderRepository.find_by_id(order_id)
        if not order:
            raise ValueError("Order not found")

        allowed = {
            "food_item",
            "order_value",
            "delivery_method",
            "restaurant_id",
            "order_time",
            "coupon_code",
        }
        invalid = set(updates.keys()) - allowed
        if invalid:
            raise ValueError(
                "Cannot update: " + ", ".join(sorted(invalid))
            )
        if not updates:
            raise ValueError("No updates provided")

        if "food_item" in updates:
            text = (updates["food_item"] or "").strip()
            if not text:
                raise ValueError("food_item cannot be empty")
            updates["food_item"] = text

        if "order_value" in updates:
            val = updates["order_value"]
            if val is None:
                raise ValueError("order_value cannot be null")
            fv = float(val)
            if fv < 0:
                raise ValueError("order_value cannot be negative")
            updates["order_value"] = fv

        if "coupon_code" in updates:
            raw = updates["coupon_code"]
            updates["coupon_code"] = OrderService._normalize_coupon_code(raw)

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
        import time
        return f"ORD-{int(time.time() * 1000)}"

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
        if source_status == OrderStatus.CANCELLED.value:
            raise ValueError("Cancelled orders cannot be reordered")

        draft_id = uuid.uuid4().hex
        fixed_km = float(settings.FIXED_DELIVERY_DISTANCE_KM)
        reorder_drafts[draft_id] = {
            "source_order_id": source_order.order_id,
            "customer_id": customer_id,
            "order_payload": {
                "restaurant_id": source_order.restaurant_id,
                "food_item": source_order.food_item,
                "order_time": source_order.order_time,
                "order_value": source_order.order_value,
                "delivery_method": source_order.delivery_method,
                "delivery_distance": fixed_km,
                "customer_id": source_order.customer_id,
                "traffic_condition": source_order.traffic_condition,
                "weather_condition": source_order.weather_condition,
                "route_taken": source_order.route_taken,
                "source_order_id": source_order.order_id,
                "coupon_code": source_order.coupon_code,
            },
        }
        return draft_id, reorder_drafts[draft_id]["order_payload"]

    @staticmethod
    def update_reorder_draft(draft_id, updates):
        draft = reorder_drafts.get(draft_id)
        if not draft:
            raise LookupError("Reorder draft not found")

        allowed_fields = {"order_time", "delivery_method"}
        invalid_fields = set(updates.keys()) - allowed_fields
        if invalid_fields:
            raise ValueError(
                "Only order_time and delivery_method can be edited"
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
        payload["delivery_distance"] = float(settings.FIXED_DELIVERY_DISTANCE_KM)
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
            coupon_code=payload.get("coupon_code"),
        )
        saved_order = OrderRepository.save(order)
        del reorder_drafts[draft_id]
        return saved_order
