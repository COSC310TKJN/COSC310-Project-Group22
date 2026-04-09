from fastapi import HTTPException

from backend.models.notification import NotificationChannel, NotificationType
from backend.repositories import notification_repo


def send_notification(user_id, notification_type, title, message,
                      order_id=None, channel=NotificationChannel.IN_APP.value):
    pref = notification_repo.get_preference(user_id, notification_type)
    if pref and not pref["enabled"]:
        return None
    if pref and pref["channel"]:
        channel = pref["channel"]
    data = {
        "user_id": user_id,
        "notification_type": notification_type,
        "channel": channel,
        "title": title,
        "message": message,
        "order_id": order_id,
    }
    return notification_repo.create_notification(data)


def notify_order_placed(user_id, order_id):
    return send_notification(
        user_id=user_id,
        notification_type=NotificationType.ORDER_PLACED.value,
        title="Order Placed",
        message=f"Your order #{order_id} has been placed successfully.",
        order_id=order_id,
    )


def notify_status_change(user_id, order_id, new_status):
    return send_notification(
        user_id=user_id,
        notification_type=NotificationType.STATUS_CHANGE.value,
        title="Order Status Updated",
        message=f"Your order #{order_id} status changed to {new_status}.",
        order_id=order_id,
    )


def notify_delivery(user_id, order_id):
    return send_notification(
        user_id=user_id,
        notification_type=NotificationType.DELIVERY.value,
        title="Order Delivered",
        message=f"Your order #{order_id} has been delivered.",
        order_id=order_id,
    )


def notify_manager_new_order(manager_id, order_id):
    return send_notification(
        user_id=manager_id,
        notification_type=NotificationType.MANAGER_NEW_ORDER.value,
        title="New Order Received",
        message=f"A new order #{order_id} has been placed at your restaurant.",
        order_id=order_id,
    )


def notify_order_cancelled(user_id, order_id):
    return send_notification(
        user_id=user_id,
        notification_type=NotificationType.ORDER_CANCELLED.value,
        title="Order Cancelled",
        message=f"Your order #{order_id} has been cancelled.",
        order_id=order_id,
    )


def get_user_notifications(user_id):
    return notification_repo.get_notifications_by_user(user_id)


def get_unread_count(user_id):
    return notification_repo.get_unread_count(user_id)


def mark_notification_read(notification_id):
    notification = notification_repo.mark_as_read(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


def _ensure_default_preferences(user_id):
    existing = notification_repo.get_preferences_by_user(user_id)
    if existing:
        return existing
    defaults = []
    for ntype in NotificationType:
        pref = notification_repo.upsert_preference(
            user_id, ntype.value, True, NotificationChannel.IN_APP.value
        )
        defaults.append(pref)
    return defaults


def get_preferences(user_id):
    return _ensure_default_preferences(user_id)


def update_preference(user_id, notification_type, enabled, channel):
    return notification_repo.upsert_preference(
        user_id, notification_type, enabled, channel)
