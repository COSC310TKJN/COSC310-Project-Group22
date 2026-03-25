from fastapi import HTTPException

from backend.models.order import Order
from backend.models.order import Order, OrderStatus
from backend.services.pricing_service import PricingService
from backend.repositories.order_repo import OrderRepository

orders_db = OrderRepository.load_orders()


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
            traffic_condition=order_data.traffic_condition,
            weather_condition=order_data.weather_condition,
            route_taken=order_data.route_taken
        )

        orders_db[order.order_id] = order

        return order

    @staticmethod
    def get_order(order_id):

        if not orders_db.get(order_id):
            return HTTPException(status_code=404, detail="Order not found")

        return orders_db.get(order_id)

    @staticmethod
    def cancel_order(order_id):

        order = orders_db.get(order_id)

        if not order:
            raise ValueError("Order not found")

        order.cancel()

        return order

    @staticmethod
    def calculate_order_total(order_id):

        order = orders_db.get(order_id)

        if not order:
            raise ValueError("Order not found")

        return PricingService.calculate_total(order)