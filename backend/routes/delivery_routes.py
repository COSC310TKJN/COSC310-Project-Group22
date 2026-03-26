from fastapi import APIRouter, Header

from backend.app.delivery_order_storage import load_status_history
from backend.models.order import OrderStatus
from backend.schemas.delivery_schema import (
    DeliveryStatusUpdateRequest,
    DeliveryStatusUpdateResponse,
    OrderCreateRequest,
    OrderStatusResponse,
    OrderTrackingResponse,
)
from backend.services import delivery_service

router = APIRouter(prefix="/orders", tags=["Delivery Tracking"])


@router.post("/", status_code=201)
def create_order(request: OrderCreateRequest):
    return delivery_service.create_delivery_order(request)


@router.get("/{order_id}/status", response_model=OrderStatusResponse)
def get_order_status(order_id: int):
    return delivery_service.get_order_status(order_id)


@router.get("/{order_id}/tracking", response_model=OrderTrackingResponse)
def get_order_tracking(order_id: int):
    return delivery_service.get_order_tracking(order_id)


@router.patch(
    "/{order_id}/status",
    response_model=DeliveryStatusUpdateResponse,
)
def update_delivery_status(
    order_id: int,
    request: DeliveryStatusUpdateRequest,
    x_role: str | None = Header(None, alias="X-Role"),
):
    order = delivery_service.update_delivery_status(
        order_id, request.new_status, role=x_role
    )
    history = load_status_history(order_id)
    last = history[-1]
    previous_status = (
        history[-2].status if len(history) >= 2 else OrderStatus.CREATED.value
    )
    cur = order.status.value if isinstance(order.status, OrderStatus) else str(order.status)
    return DeliveryStatusUpdateResponse(
        order_id=order_id,
        previous_status=previous_status,
        new_status=cur,
        updated_at=last.updated_at,
        updated_by_role=last.updated_by_role,
    )
