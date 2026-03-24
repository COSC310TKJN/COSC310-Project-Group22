from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.schemas.notification_schema import NotificationResponse, PreferenceResponse
from backend.services import notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=list[NotificationResponse])
def get_notifications(user_id: str, db: Session = Depends(get_db)):
    return notification_service.get_user_notifications(db, user_id)


@router.get("/unread/count")
def get_unread_count(user_id: str, db: Session = Depends(get_db)):
    count = notification_service.get_unread_count(db, user_id)
    return {"user_id": user_id, "unread_count": count}


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_as_read(notification_id: int, db: Session = Depends(get_db)):
    return notification_service.mark_notification_read(db, notification_id)


@router.post("/order-placed", status_code=201)
def notify_order_placed(user_id: str, order_id: int, db: Session = Depends(get_db)):
    result = notification_service.notify_order_placed(db, user_id, order_id)
    if not result:
        return {"message": "notification disabled by preference"}
    return result


@router.post("/status-change", status_code=201)
def notify_status_change(user_id: str, order_id: int, new_status: str, db: Session = Depends(get_db)):
    result = notification_service.notify_status_change(db, user_id, order_id, new_status)
    if not result:
        return {"message": "notification disabled by preference"}
    return result


@router.post("/delivery", status_code=201)
def notify_delivery(user_id: str, order_id: int, db: Session = Depends(get_db)):
    result = notification_service.notify_delivery(db, user_id, order_id)
    if not result:
        return {"message": "notification disabled by preference"}
    return result


@router.post("/manager/new-order", status_code=201)
def notify_manager_new_order(manager_id: str, order_id: int, db: Session = Depends(get_db)):
    result = notification_service.notify_manager_new_order(db, manager_id, order_id)
    if not result:
        return {"message": "notification disabled by preference"}
    return result


@router.post("/order-cancelled", status_code=201)
def notify_order_cancelled(user_id: str, order_id: int, db: Session = Depends(get_db)):
    result = notification_service.notify_order_cancelled(db, user_id, order_id)
    if not result:
        return {"message": "notification disabled by preference"}
    return result


@router.get("/preferences", response_model=list[PreferenceResponse])
def get_preferences(user_id: str, db: Session = Depends(get_db)):
    return notification_service.get_preferences(db, user_id)


@router.put("/preferences", response_model=PreferenceResponse)
def update_preference(user_id: str, notification_type: str, enabled: bool = True, channel: str = "in_app", db: Session = Depends(get_db)):
    return notification_service.update_preference(db, user_id, notification_type, enabled, channel)
