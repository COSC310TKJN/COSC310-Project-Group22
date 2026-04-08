from enum import Enum


class OrderStatus(str, Enum):
    CREATED = "created"
    PAID = "paid"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Order:
    def __init__(
        self,
        order_id: str,
        restaurant_id: int,
        food_item: str,
        order_time: str,
        order_value: float,
        delivery_method: str,
        delivery_distance: float,
        customer_id: str,
        source_order_id: str = None,
        traffic_condition: str = None,
        weather_condition: str = None,
        route_taken: str = None,
        coupon_code: str = None
    ):

        if not order_id:
            raise ValueError("Order must provide an ID")

        if not customer_id:
            raise ValueError("User must be authenticated to place an order")

        if order_value < 0:
            raise ValueError("Price cannot be negative")

        if not food_item:
            raise ValueError("Order must include a food item")

        self.order_id = order_id
        self.restaurant_id = restaurant_id
        self.food_item = food_item
        self.order_time = order_time
        self.order_value = order_value
        self.delivery_method = delivery_method
        self.delivery_distance = delivery_distance
        self.customer_id = customer_id
        self.source_order_id = source_order_id
        self.traffic_condition = traffic_condition
        self.weather_condition = weather_condition
        self.route_taken = route_taken
        self.coupon_code = coupon_code

        self.status = OrderStatus.CREATED

    def mark_paid(self):

        if self.status != OrderStatus.CREATED:
            raise ValueError("Order can only be placed once")

        self.status = OrderStatus.PAID

    def prep_order(self):

        if self.status != OrderStatus.PAID:
            raise ValueError("Order must be paid prior to preparation")

        self.status = OrderStatus.PREPARING

    def send_out_delivery(self):

        if self.status != OrderStatus.PREPARING:
            raise ValueError("Order must be prepared before delivery")

        self.status = OrderStatus.OUT_FOR_DELIVERY

    def mark_delivered(self):

        if self.status != OrderStatus.OUT_FOR_DELIVERY:
            raise ValueError("Order must be out for delivery")

        self.status = OrderStatus.DELIVERED

    def cancel(self):

        if self.status == OrderStatus.PREPARING:
            raise ValueError("Cannot cancel an order that is already being prepared")

        self.status = OrderStatus.CANCELLED

    def to_dict(self):

        return {
            "order_id": self.order_id,
            "restaurant_id": self.restaurant_id,
            "food_item": self.food_item,
            "customer_id": self.customer_id,
            "order_time": self.order_time,
            "order_value": self.order_value,
            "delivery_method": self.delivery_method,
            "delivery_distance": self.delivery_distance,
            "traffic_condition": self.traffic_condition,
            "weather_condition": self.weather_condition,
            "route_taken": self.route_taken,
            "source_order_id": self.source_order_id,
            "coupon_code": self.coupon_code,
            "status": self.status
        }