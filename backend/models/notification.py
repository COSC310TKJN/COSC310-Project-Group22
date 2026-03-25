from enum import Enum


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
