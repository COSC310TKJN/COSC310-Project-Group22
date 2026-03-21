from sqlalchemy.orm import Session

from backend.models.notification import Notification
from backend.models.notification_preference import NotificationPreference


def create_notification(db: Session, notification: Notification) -> Notification:
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_notifications_by_user(db: Session, user_id: str):
    return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()


def get_unread_count(db: Session, user_id: str) -> int:
    return db.query(Notification).filter(Notification.user_id == user_id, Notification.is_read == False).count()


def mark_as_read(db: Session, notification_id: int) -> Notification | None:
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if notification:
        notification.is_read = True
        db.commit()
        db.refresh(notification)
    return notification


def get_preference(db: Session, user_id: str, notification_type: str):
    return db.query(NotificationPreference).filter(
        NotificationPreference.user_id == user_id,
        NotificationPreference.notification_type == notification_type,
    ).first()


def get_preferences_by_user(db: Session, user_id: str):
    return db.query(NotificationPreference).filter(NotificationPreference.user_id == user_id).all()


def upsert_preference(db: Session, user_id: str, notification_type: str, enabled: bool, channel: str):
    pref = get_preference(db, user_id, notification_type)
    if pref:
        pref.enabled = enabled
        pref.channel = channel
    else:
        pref = NotificationPreference(user_id=user_id, notification_type=notification_type, enabled=enabled, channel=channel)
        db.add(pref)
    db.commit()
    db.refresh(pref)
    return pref
