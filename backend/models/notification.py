from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from backend.app.database import Base


class NotificationType(str, Enum):
    ORDER_PLACED = "order_placed"
    STATUS_CHANGE = "status_change"
    ORDER_CANCELLED = "order_cancelled"
    DELIVERY = "delivery"
    MANAGER_NEW_ORDER = "manager_new_order"


class NotificationChannel(str, Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    notification_type = Column(String, nullable=False)
    channel = Column(String, nullable=False, default=NotificationChannel.IN_APP.value)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    order_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
