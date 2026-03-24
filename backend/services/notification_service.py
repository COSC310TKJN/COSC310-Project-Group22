from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.notification import Notification, NotificationChannel, NotificationType
from backend.repositories import notification_repo


def send_notification(db: Session, user_id: str, notification_type: str, title: str, message: str, order_id: int = None, channel: str = NotificationChannel.IN_APP.value):
    notification = Notification(
        user_id=user_id,
        notification_type=notification_type,
        channel=channel,
        title=title,
        message=message,
        order_id=order_id,
    )
    return notification_repo.create_notification(db, notification)


def notify_order_placed(db: Session, user_id: str, order_id: int):
    return send_notification(
        db,
        user_id=user_id,
        notification_type=NotificationType.ORDER_PLACED.value,
        title="Order Placed",
        message=f"Your order #{order_id} has been placed successfully.",
        order_id=order_id,
    )


def get_user_notifications(db: Session, user_id: str):
    return notification_repo.get_notifications_by_user(db, user_id)


def get_unread_count(db: Session, user_id: str):
    return notification_repo.get_unread_count(db, user_id)


def mark_notification_read(db: Session, notification_id: int):
    notification = notification_repo.mark_as_read(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification
