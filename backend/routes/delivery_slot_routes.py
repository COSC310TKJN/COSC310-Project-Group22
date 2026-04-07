from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, Query

from backend.app.routes.auth_routes import require_manager
from backend.models.user import User
from backend.schemas.delivery_slot_schema import (
    DeliveryBlackoutCreateRequest,
    DeliveryBlackoutResponse,
    DeliverySlotAvailabilityResponse,
    DeliverySlotBookingResponse,
    DeliverySlotConfigResponse,
    DeliverySlotConfigUpdateRequest,
    DeliverySlotSelectionRequest,
    DriverAssignmentRequest,
    DriverAssignmentResponse,
    DriverQueueResponse,
)
from backend.services import delivery_slot_service

router = APIRouter(tags=["Delivery Slot Management"])


@router.get(
    "/restaurants/{restaurant_id}/delivery-slots/availability",
    response_model=DeliverySlotAvailabilityResponse,
)
def get_delivery_slot_availability(
    restaurant_id: int,
    date: str | None = Query(default=None, description="YYYY-MM-DD"),
):
    target_date = date or datetime.now(timezone.utc).date().isoformat()
    return delivery_slot_service.get_slot_availability(restaurant_id, target_date)


@router.post(
    "/orders/{order_id}/delivery-slot",
    response_model=DeliverySlotBookingResponse,
    status_code=201,
)
def select_delivery_slot(order_id: str, payload: DeliverySlotSelectionRequest):
    return delivery_slot_service.select_delivery_slot(order_id, payload.slot_start)


@router.post(
    "/delivery-slots/assignments",
    response_model=DriverAssignmentResponse,
    status_code=201,
)
def assign_delivery_slot(
    payload: DriverAssignmentRequest,
    x_role: str | None = Header(default=None, alias="X-Role"),
):
    return delivery_slot_service.assign_driver(
        order_id=payload.order_id,
        driver_id=payload.driver_id,
        role=x_role,
    )


@router.get("/drivers/{driver_id}/delivery-queue", response_model=DriverQueueResponse)
def get_driver_delivery_queue(
    driver_id: str,
    date: str | None = Query(default=None, description="YYYY-MM-DD"),
):
    return delivery_slot_service.get_driver_queue(driver_id, date_value=date)


@router.put(
    "/admin/restaurants/{restaurant_id}/delivery-slot-config",
    response_model=DeliverySlotConfigResponse,
)
def update_slot_config(
    restaurant_id: int,
    payload: DeliverySlotConfigUpdateRequest,
    current_user: User = Depends(require_manager),
):
    return delivery_slot_service.upsert_slot_config(
        restaurant_id=restaurant_id,
        slot_duration_minutes=payload.slot_duration_minutes,
        slot_capacity=payload.slot_capacity,
    )


@router.post(
    "/admin/restaurants/{restaurant_id}/delivery-blackouts",
    response_model=DeliveryBlackoutResponse,
    status_code=201,
)
def create_delivery_blackout(
    restaurant_id: int,
    payload: DeliveryBlackoutCreateRequest,
    current_user: User = Depends(require_manager),
):
    return delivery_slot_service.create_blackout(
        restaurant_id=restaurant_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        reason=payload.reason,
    )


@router.get(
    "/admin/restaurants/{restaurant_id}/delivery-blackouts",
    response_model=list[DeliveryBlackoutResponse],
)
def list_delivery_blackouts(
    restaurant_id: int,
    date: str | None = Query(default=None, description="YYYY-MM-DD"),
    current_user: User = Depends(require_manager),
):
    return delivery_slot_service.list_blackouts(restaurant_id=restaurant_id, date_value=date)
