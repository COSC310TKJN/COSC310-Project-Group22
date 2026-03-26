from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from backend.models.order import OrderStatus


class DeliveryStatusUpdate:
    order_id: int
    status: str
    update_time: datetime
    updated_by: str | None = None
    id: int | None = None


class OrderDB:
    id: int
    customer_id: str
    current_status: str = OrderStatus.CREATED.value
    restaurant_id: int | None = None
    food_item: str | None = None
    order_value: float | None = None
    order_time: datetime | None = None
    update_time: datetime | None = None
    status_history: list[DeliveryStatusUpdate] = field(default_factory=list)


