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

    coupon_code: Optional[str] = None

    source_order_id: Optional[str] = None
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
    source_order_id: Optional[str] = None
    status: str


class ReorderDraftRequest(BaseModel):
    customer_id: str


class ReorderDraftUpdate(BaseModel):
    order_time: Optional[str] = None
    delivery_method: Optional[str] = None
    delivery_distance: Optional[float] = None
