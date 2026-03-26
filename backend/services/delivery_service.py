from datetime import datetime, timezone

from fastapi import HTTPException

from backend.app.delivery_order_storage import append_status, load_status_history
from backend.models.order import Order, OrderStatus
from backend.repositories import order_repo
from backend.schemas.delivery_schema import (
    AUTHORIZED_ROLES,
    DeliveryStatusUpdateEntry,
    OrderCreateRequest,
    OrderResponse,
    OrderStatusResponse,
    OrderTrackingResponse,
)


def _order_time_as_dt(order):
    t = order.order_time
    if isinstance(t, datetime):
        return t
    s = str(t).strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return datetime.fromisoformat(s)


def _next_numeric_order_id():
    m = 0
    for o in order_repo.OrderRepository.find_all():
        try:
            m = max(m, int(o.order_id))
        except ValueError:
            continue
    return m + 1


def order_to_response(order):
    oid = int(order.order_id)
    t = _order_time_as_dt(order)
    st = order.status.value if isinstance(order.status, OrderStatus) else str(order.status)
    return OrderResponse(
        id=oid,
        customer_id=order.customer_id,
        current_status=st,
        restaurant_id=order.restaurant_id,
        food_item=order.food_item,
        order_value=order.order_value,
        created_at=t,
        updated_at=t,
    )


def create_delivery_order(request):
    nid = _next_numeric_order_id()
    oid = str(nid)
    now = datetime.now(timezone.utc).isoformat()
    restaurant_id = int(request.restaurant_id) if request.restaurant_id is not None else 0
    food_item = (request.food_item or "").strip() or "Unspecified"
    order_value = float(request.order_value) if request.order_value is not None else 0.0
    order = Order(
        order_id=oid,
        restaurant_id=restaurant_id,
        food_item=food_item,
        order_time=now,
        order_value=order_value,
        delivery_method="bike",
        delivery_distance=0.0,
        customer_id=request.customer_id,
    )
    order_repo.OrderRepository.save(order)
    append_status(nid, OrderStatus.CREATED.value, None)
    return order_to_response(order)


def get_order_status(order_id):
    order = order_repo.OrderRepository.find_by_id(str(order_id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    hist = load_status_history(order_id)
    updated_at = hist[-1].updated_at if hist else _order_time_as_dt(order)
    st = order.status.value if isinstance(order.status, OrderStatus) else str(order.status)
    return OrderStatusResponse(
        order_id=order_id,
        current_status=st,
        updated_at=updated_at,
    )


def get_order_tracking(order_id):
    order = order_repo.OrderRepository.find_by_id(str(order_id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    history = load_status_history(order_id)
    st = order.status.value if isinstance(order.status, OrderStatus) else str(order.status)
    created_at = history[0].updated_at if history else _order_time_as_dt(order)
    updated_at = history[-1].updated_at if history else _order_time_as_dt(order)
    return OrderTrackingResponse(
        order_id=order_id,
        customer_id=order.customer_id,
        current_status=st,
        restaurant_id=order.restaurant_id,
        food_item=order.food_item,
        created_at=created_at,
        updated_at=updated_at,
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
    order_id,
    new_status,
    role,
):
    if role is None or role.lower() not in AUTHORIZED_ROLES:
        raise HTTPException(
            status_code=403,
            detail="User Unauthorized: only drivers or administrators can update delivery status",
        )
    order = order_repo.OrderRepository.find_by_id(str(order_id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    cur = order.status.value if isinstance(order.status, OrderStatus) else str(order.status)
    if cur == OrderStatus.DELIVERED.value:
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
    allowed = valid_transitions.get(cur, [])
    if new_status.value not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot update {cur} to {new_status.value}",
        )
    order.status = new_status
    order_repo.OrderRepository.save(order)
    append_status(order_id, new_status.value, role.lower())
    return order
