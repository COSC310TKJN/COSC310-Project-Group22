from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: int
    user_id: str
    notification_type: str
    channel: str
    title: str
    message: str
    is_read: bool
    order_id: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
