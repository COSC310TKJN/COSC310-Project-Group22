from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReceiptResponse(BaseModel):
    id: int
    payment_id: int
    order_id: int
    customer_id: str
    receipt_number: str
    amount: float
    tax: float
    total: float
    payment_method: str
    issued_at: Optional[datetime] = None
