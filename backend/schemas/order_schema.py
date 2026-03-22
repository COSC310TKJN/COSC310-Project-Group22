from pydantic import BaseModel
from typing import Optional
from enum import Enum


class OrderStatus(str, Enum):
    CREATED = "created"
    PAID = "paid"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderCreate(BaseModel):

    order_id: str
    restaurant_id: int
    food_item: str
    order_time: str
    order_value: float
    delivery_method: str
    delivery_distance: float
    customer_id: str

    traffic_condition: Optional[str] = None
    weather_condition: Optional[str] = None
    route_taken: Optional[str] = None


class OrderResponse(BaseModel):

    order_id: str
    restaurant_id: int
    food_item: str
    order_time: str
    order_value: float
    delivery_method: str
    delivery_distance: float
    customer_id: str
    status: str