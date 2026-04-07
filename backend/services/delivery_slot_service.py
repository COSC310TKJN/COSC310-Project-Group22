from datetime import date, datetime, time, timedelta, timezone

from fastapi import HTTPException

from backend.models.order import OrderStatus
from backend.repositories import delivery_slot_repo, order_repo, restaurant_repo
from backend.services.order_service import OrderService

DEFAULT_SLOT_DURATION_MINUTES = 60
DEFAULT_SLOT_CAPACITY = 3
OPEN_HOUR = 10
CLOSE_HOUR = 22
AUTHORIZED_ASSIGNMENT_ROLES = frozenset({"driver", "admin"})
BLOCKED_ORDER_STATUSES = {
    OrderStatus.CANCELLED.value,
    OrderStatus.DELIVERED.value,
    OrderStatus.COMPLETED.value,
}


def _parse_iso_datetime(value):
    raw = value.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _parse_date(value):
    return date.fromisoformat(value)


def _order_status_value(order):
    return order.status.value if hasattr(order.status, "value") else str(order.status)


def _find_order(order_id):
    order = order_repo.OrderRepository.find_by_id(str(order_id))
    if order:
        return order
    return OrderService.get_order(str(order_id))


def _ensure_restaurant_exists(restaurant_id):
    restaurant = restaurant_repo.get_restaurant_by_id(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant


def _load_config(restaurant_id):
    cfg = delivery_slot_repo.get_slot_config_by_restaurant(restaurant_id)
    if cfg:
        return cfg
    return {
        "restaurant_id": restaurant_id,
        "slot_duration_minutes": DEFAULT_SLOT_DURATION_MINUTES,
        "slot_capacity": DEFAULT_SLOT_CAPACITY,
    }


def _slot_overlaps_blackout(slot_start, slot_end, blackout):
    blackout_start = _parse_iso_datetime(blackout["start_time"])
    blackout_end = _parse_iso_datetime(blackout["end_time"])
    return slot_start < blackout_end and blackout_start < slot_end


def _bookings_for_day(restaurant_id, target_day):
    bookings = []
    for booking in delivery_slot_repo.get_bookings_by_restaurant(restaurant_id):
        slot_start = _parse_iso_datetime(booking["slot_start"])
        if slot_start.date() == target_day:
            bookings.append(booking)
    return bookings


def _generate_slots_for_day(restaurant_id, target_day):
    cfg = _load_config(restaurant_id)
    duration = cfg["slot_duration_minutes"]
    capacity = cfg["slot_capacity"]
    blackouts = delivery_slot_repo.get_blackouts_by_restaurant(restaurant_id)
    bookings = _bookings_for_day(restaurant_id, target_day)

    window_start = datetime.combine(target_day, time(hour=OPEN_HOUR), tzinfo=timezone.utc)
    window_end = datetime.combine(target_day, time(hour=CLOSE_HOUR), tzinfo=timezone.utc)
    cursor = window_start
    delta = timedelta(minutes=duration)
    slots = []

    while cursor + delta <= window_end:
        slot_start = cursor
        slot_end = cursor + delta
        matching_bookings = [
            b for b in bookings if _parse_iso_datetime(b["slot_start"]) == slot_start
        ]
        remaining_capacity = max(capacity - len(matching_bookings), 0)

        disabled_reason = None
        for blackout in blackouts:
            if _slot_overlaps_blackout(slot_start, slot_end, blackout):
                disabled_reason = "blackout"
                break
        if disabled_reason is None and remaining_capacity <= 0:
            disabled_reason = "full"

        slots.append(
            {
                "slot_start": slot_start.isoformat(),
                "slot_end": slot_end.isoformat(),
                "is_available": disabled_reason is None,
                "remaining_capacity": remaining_capacity if disabled_reason != "blackout" else 0,
                "disabled_reason": disabled_reason,
            }
        )
        cursor += delta

    return {
        "restaurant_id": restaurant_id,
        "date": target_day.isoformat(),
        "slot_duration_minutes": duration,
        "slot_capacity": capacity,
        "slots": slots,
    }


def get_slot_availability(restaurant_id, date_value):
    _ensure_restaurant_exists(restaurant_id)
    target_day = _parse_date(date_value)
    return _generate_slots_for_day(restaurant_id, target_day)


def select_delivery_slot(order_id, slot_start_value):
    order = _find_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    restaurant_id = int(order.restaurant_id)
    _ensure_restaurant_exists(restaurant_id)

    order_status = _order_status_value(order)
    if order_status in BLOCKED_ORDER_STATUSES:
        raise HTTPException(status_code=400, detail="Order can no longer be booked")

    selected_start = _parse_iso_datetime(slot_start_value)
    availability = _generate_slots_for_day(restaurant_id, selected_start.date())
    selected_slot = next(
        (slot for slot in availability["slots"] if slot["slot_start"] == selected_start.isoformat()),
        None,
    )
    if selected_slot is None:
        raise HTTPException(status_code=400, detail="Selected slot is outside restaurant delivery hours")
    if not selected_slot["is_available"]:
        reason = selected_slot["disabled_reason"] or "unavailable"
        raise HTTPException(status_code=409, detail=f"Selected slot is unavailable ({reason})")

    booking = delivery_slot_repo.upsert_slot_booking(
        order_id=str(order_id),
        restaurant_id=restaurant_id,
        slot_start=selected_slot["slot_start"],
        slot_end=selected_slot["slot_end"],
        status="scheduled",
    )
    return booking


def upsert_slot_config(restaurant_id, slot_duration_minutes, slot_capacity):
    _ensure_restaurant_exists(restaurant_id)
    return delivery_slot_repo.upsert_slot_config(
        restaurant_id=restaurant_id,
        slot_duration_minutes=slot_duration_minutes,
        slot_capacity=slot_capacity,
    )


def create_blackout(restaurant_id, start_time, end_time, reason):
    _ensure_restaurant_exists(restaurant_id)
    start_dt = _parse_iso_datetime(start_time)
    end_dt = _parse_iso_datetime(end_time)
    if end_dt <= start_dt:
        raise HTTPException(status_code=400, detail="end time must be after start time")

    return delivery_slot_repo.create_blackout(
        restaurant_id=restaurant_id,
        start_time=start_dt.isoformat(),
        end_time=end_dt.isoformat(),
        reason=reason,
    )


def list_blackouts(restaurant_id, date_value=None):
    _ensure_restaurant_exists(restaurant_id)
    rows = delivery_slot_repo.get_blackouts_by_restaurant(restaurant_id)
    if date_value is None:
        return rows

    target_day = _parse_date(date_value)
    result = []
    for row in rows:
        start = _parse_iso_datetime(row["start_time"])
        end = _parse_iso_datetime(row["end_time"])
        if start.date() <= target_day <= end.date():
            result.append(row)
    return result


def assign_driver(order_id, driver_id, role):
    if role is None or role.lower() not in AUTHORIZED_ASSIGNMENT_ROLES:
        raise HTTPException(
            status_code=403,
            detail="User Unauthorized: only drivers or admins can assign deliveries",
        )

    booking = delivery_slot_repo.get_booking_by_order_id(order_id)
    if not booking:
        raise HTTPException(status_code=400, detail="Order has no scheduled delivery slot")

    assignment = delivery_slot_repo.upsert_driver_assignment(order_id=order_id, driver_id=driver_id)
    return {
        "id": assignment["id"],
        "order_id": assignment["order_id"],
        "driver_id": assignment["driver_id"],
        "assigned_at": assignment["assigned_at"],
        "slot_start": booking["slot_start"],
        "slot_end": booking["slot_end"],
    }


def get_driver_queue(driver_id, date_value=None):
    assignments = delivery_slot_repo.get_assignments_by_driver(driver_id)
    items = []
    target_day = _parse_date(date_value) if date_value else None

    for assignment in assignments:
        booking = delivery_slot_repo.get_booking_by_order_id(assignment["order_id"])
        if not booking:
            continue
        slot_start = _parse_iso_datetime(booking["slot_start"])
        if target_day and slot_start.date() != target_day:
            continue
        items.append(
            {
                "order_id": booking["order_id"],
                "restaurant_id": booking["restaurant_id"],
                "slot_start": booking["slot_start"],
                "slot_end": booking["slot_end"],
                "booking_status": booking["status"],
            }
        )

    items.sort(key=lambda item: (_parse_iso_datetime(item["slot_start"]), item["order_id"]))
    return {"driver_id": driver_id, "items": items}
