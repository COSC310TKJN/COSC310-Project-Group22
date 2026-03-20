from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from backend.models.order import OrderStatus

class OrderStatusResponse(BaseModel):
    order_id: int
    current_status: str
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DeliveryStatusUpdateEntry(BaseModel):
    status: str
    updated_at: datetime
    updated_by_role: Optional[str] = None
    model_config = {"from_attributes": True}


class OrderTrackingResponse(BaseModel):
    order_id: int
    customer_id: str
    current_status: str
    restaurant_id: Optional[int] = None
    food_item: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    status_history: list[DeliveryStatusUpdateEntry] = []

    model_config = {"from_attributes": True}

AUTHORIZED_ROLES = frozenset({"driver", "admin"})


class DeliveryStatusUpdateRequest(BaseModel):
    new_status: OrderStatus = Field(..., description="Target delivery status")

class DeliveryStatusUpdateResponse(BaseModel):
    order_id: int
    previous_status: str
    new_status: str
    updated_at: datetime
    updated_by_role: Optional[str] = None

    model_config = {"from_attributes": True}


class OrderCreateRequest(BaseModel):
    customer_id: str = Field(..., min_length=1)
    restaurant_id: Optional[int] = None
    food_item: Optional[str] = None
    order_value: Optional[float] = Field(None, ge=0)


class OrderResponse(BaseModel):
    id: int
    customer_id: str
    current_status: str
    restaurant_id: Optional[int] = None
    food_item: Optional[str] = None
    order_value: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
