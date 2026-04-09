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
    order_id: Optional[str] = None
    created_at: Optional[datetime] = None


class PreferenceRequest(BaseModel):
    notification_type: str
    enabled: bool = True
    channel: str = "in_app"


class PreferenceResponse(BaseModel):
    id: int
    user_id: str
    notification_type: str
    enabled: bool
    channel: str
