from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from backend.models.payment import PaymentMethod


class PaymentRequest(BaseModel):
    order_id: int
    customer_id: str
    amount: float = Field(gt=0)
    payment_method: PaymentMethod


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    customer_id: str
    amount: float
    payment_method: str
    status: str
    transaction_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PaymentStatusResponse(BaseModel):
    id: int
    order_id: int
    status: str
    transaction_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
