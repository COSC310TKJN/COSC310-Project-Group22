from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.schemas.notification_schema import NotificationResponse
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


@router.post("/order-placed", response_model=NotificationResponse, status_code=201)
def notify_order_placed(user_id: str, order_id: int, db: Session = Depends(get_db)):
    return notification_service.notify_order_placed(db, user_id, order_id)


@router.post("/status-change", response_model=NotificationResponse, status_code=201)
def notify_status_change(user_id: str, order_id: int, new_status: str, db: Session = Depends(get_db)):
    return notification_service.notify_status_change(db, user_id, order_id, new_status)


@router.post("/delivery", response_model=NotificationResponse, status_code=201)
def notify_delivery(user_id: str, order_id: int, db: Session = Depends(get_db)):
    return notification_service.notify_delivery(db, user_id, order_id)


@router.post("/manager/new-order", response_model=NotificationResponse, status_code=201)
def notify_manager_new_order(manager_id: str, order_id: int, db: Session = Depends(get_db)):
    return notification_service.notify_manager_new_order(db, manager_id, order_id)
