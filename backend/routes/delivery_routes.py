from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.models.order import OrderStatus
from backend.repositories import order_repo
from backend.schemas.delivery_schema import (
    DeliveryStatusUpdateRequest,
    DeliveryStatusUpdateResponse,
    OrderCreateRequest,
    OrderResponse,
    OrderStatusResponse,
    OrderTrackingResponse,
)
from backend.services import delivery_service

router = APIRouter(prefix="/orders", tags=["Delivery Tracking"])


@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(request: OrderCreateRequest, db: Session = Depends(get_db)):
    """Create an order for delivery tracking (lifecycle starts at CREATED)."""
    order = order_repo.create_order(
        db,
        customer_id=request.customer_id,
        restaurant_id=request.restaurant_id,
        food_item=request.food_item,
        order_value=request.order_value,
    )
    return order


@router.get("/{order_id}/status", response_model=OrderStatusResponse)
def get_order_status(order_id: int, db: Session = Depends(get_db)):
    return delivery_service.get_order_status(db, order_id)


@router.get("/{order_id}/tracking", response_model=OrderTrackingResponse)
def get_order_tracking(order_id: int, db: Session = Depends(get_db)):
    return delivery_service.get_order_tracking(db, order_id)


@router.patch(
    "/{order_id}/status",
    response_model=DeliveryStatusUpdateResponse,
)
def update_delivery_status(
    order_id: int,
    request: DeliveryStatusUpdateRequest,
    db: Session = Depends(get_db),
    x_role: str | None = Header(None, alias="X-Role"),
):
  
    order = delivery_service.update_delivery_status(
        db, order_id, request.new_status, role=x_role
    )
    history = order_repo.get_status_history(db, order.id)
    last = history[-1] if history else None
    previous_status = (
        history[-2].status if len(history) >= 2 else OrderStatus.CREATED.value
    )
  
    return DeliveryStatusUpdateResponse(
        order_id=order.id,
        previous_status=previous_status,
        new_status=order.current_status,
        updated_at=last.updated_at if last else order.updated_at,
        updated_by_role=last.updated_by_role if last else None,
    )
