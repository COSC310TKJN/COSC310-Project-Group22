from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.models.delivery import OrderDB
from backend.models.order import OrderStatus
from backend.repositories import order_repo
from backend.schemas.delivery_schema import (
    AUTHORIZED_ROLES,
    DeliveryStatusUpdateEntry,
    OrderStatusResponse,
    OrderTrackingResponse,
)


def get_order_status(db: Session, order_id: int) -> OrderStatusResponse:
    order = order_repo.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderStatusResponse(
        order_id=order.id,
        current_status=order.current_status,
        updated_at=order.updated_at,
    )


def get_order_tracking(db: Session, order_id: int) -> OrderTrackingResponse:
    order = order_repo.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    history = order_repo.get_status_history(db, order_id)
    return OrderTrackingResponse(
        order_id=order.id,
        customer_id=order.customer_id,
        current_status=order.current_status,
        restaurant_id=order.restaurant_id,
        food_item=order.food_item,
        created_at=order.created_at,
        updated_at=order.updated_at,
        status_history=[
            DeliveryStatusUpdateEntry(
                status=e.status,
                updated_at=e.updated_at,
                updated_by_role=e.updated_by_role,
            )
            for e in history
        ],
    )


def update_delivery_status(
    db: Session,
    order_id: int,
    new_status: OrderStatus,
    role: str | None,
) -> OrderDB:
    if role is None or role.lower() not in AUTHORIZED_ROLES:
        raise HTTPException(
            status_code=403,
            detail="User Unauthorized: only drivers or administrators can update delivery status",
        )
    order = order_repo.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.current_status == OrderStatus.DELIVERED.value:
        raise HTTPException(
            status_code=400,
            detail="Delivered orders cannot be updated",
        )
    valid_transitions = {
        OrderStatus.CREATED.value: [OrderStatus.PAID.value, OrderStatus.CANCELLED.value],
        OrderStatus.PAID.value: [OrderStatus.PREPARING.value, OrderStatus.CANCELLED.value],
        OrderStatus.PREPARING.value: [OrderStatus.OUT_FOR_DELIVERY.value],
        OrderStatus.OUT_FOR_DELIVERY.value: [OrderStatus.DELIVERED.value],
        OrderStatus.CANCELLED.value: [],
    }
    allowed = valid_transitions.get(order.current_status, [])
    if new_status.value not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot update {order.current_status} to {new_status.value}",
        )
    return order_repo.update_order_status(
        db, order, new_status.value, updated_by_role=role.lower()
    )
