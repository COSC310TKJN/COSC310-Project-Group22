import csv
import os
from datetime import datetime
from pathlib import Path

from backend.app import csv_storage

SLOT_CONFIG_HEADERS = [
    "id",
    "restaurant_id",
    "slot_duration_minutes",
    "slot_capacity",
]

SLOT_BLACKOUT_HEADERS = [
    "id",
    "restaurant_id",
    "start_time",
    "end_time",
    "reason",
]

SLOT_BOOKING_HEADERS = [
    "id",
    "order_id",
    "restaurant_id",
    "slot_start",
    "slot_end",
    "status",
    "created_at",
]

DRIVER_ASSIGNMENT_HEADERS = [
    "id",
    "order_id",
    "driver_id",
    "assigned_at",
]


def get_slot_configs_csv_path():
    return Path(
        os.environ.get("DELIVERY_SLOT_CONFIGS_CSV_PATH", "data/delivery_slot_configs.csv")
    )


def get_slot_blackouts_csv_path():
    return Path(
        os.environ.get("DELIVERY_SLOT_BLACKOUTS_CSV_PATH", "data/delivery_slot_blackouts.csv")
    )


def get_slot_bookings_csv_path():
    return Path(
        os.environ.get("DELIVERY_SLOT_BOOKINGS_CSV_PATH", "data/delivery_slot_bookings.csv")
    )


def get_driver_assignments_csv_path():
    return Path(
        os.environ.get(
            "DELIVERY_SLOT_DRIVER_ASSIGNMENTS_CSV_PATH",
            "data/delivery_slot_driver_assignments.csv",
        )
    )


def _read(path, headers):
    return csv_storage.read_rows(path, headers)


def _write(path, headers, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def _config_row_to_dict(row):
    return {
        "id": int(row["id"]),
        "restaurant_id": int(row["restaurant_id"]),
        "slot_duration_minutes": int(row["slot_duration_minutes"]),
        "slot_capacity": int(row["slot_capacity"]),
    }


def _config_to_row(data):
    return {
        "id": str(data["id"]),
        "restaurant_id": str(data["restaurant_id"]),
        "slot_duration_minutes": str(data["slot_duration_minutes"]),
        "slot_capacity": str(data["slot_capacity"]),
    }


def _blackout_row_to_dict(row):
    return {
        "id": int(row["id"]),
        "restaurant_id": int(row["restaurant_id"]),
        "start_time": row["start_time"],
        "end_time": row["end_time"],
        "reason": row["reason"] or None,
    }


def _blackout_to_row(data):
    return {
        "id": str(data["id"]),
        "restaurant_id": str(data["restaurant_id"]),
        "start_time": data["start_time"],
        "end_time": data["end_time"],
        "reason": data["reason"] or "",
    }


def _booking_row_to_dict(row):
    return {
        "id": int(row["id"]),
        "order_id": row["order_id"],
        "restaurant_id": int(row["restaurant_id"]),
        "slot_start": row["slot_start"],
        "slot_end": row["slot_end"],
        "status": row["status"],
        "created_at": row["created_at"],
    }


def _booking_to_row(data):
    return {
        "id": str(data["id"]),
        "order_id": str(data["order_id"]),
        "restaurant_id": str(data["restaurant_id"]),
        "slot_start": data["slot_start"],
        "slot_end": data["slot_end"],
        "status": data["status"],
        "created_at": data["created_at"],
    }


def _assignment_row_to_dict(row):
    return {
        "id": int(row["id"]),
        "order_id": row["order_id"],
        "driver_id": row["driver_id"],
        "assigned_at": row["assigned_at"],
    }


def _assignment_to_row(data):
    return {
        "id": str(data["id"]),
        "order_id": str(data["order_id"]),
        "driver_id": data["driver_id"],
        "assigned_at": data["assigned_at"],
    }


def get_slot_config_by_restaurant(restaurant_id):
    for row in _read(get_slot_configs_csv_path(), SLOT_CONFIG_HEADERS):
        config = _config_row_to_dict(row)
        if config["restaurant_id"] == restaurant_id:
            return config
    return None


def upsert_slot_config(restaurant_id, slot_duration_minutes, slot_capacity):
    path = get_slot_configs_csv_path()
    rows = _read(path, SLOT_CONFIG_HEADERS)

    for row in rows:
        if int(row["restaurant_id"]) == restaurant_id:
            row["slot_duration_minutes"] = str(slot_duration_minutes)
            row["slot_capacity"] = str(slot_capacity)
            _write(path, SLOT_CONFIG_HEADERS, rows)
            return _config_row_to_dict(row)

    config = {
        "id": csv_storage.next_int_id(rows),
        "restaurant_id": restaurant_id,
        "slot_duration_minutes": slot_duration_minutes,
        "slot_capacity": slot_capacity,
    }
    csv_storage.append_row(path, SLOT_CONFIG_HEADERS, _config_to_row(config))
    return config


def create_blackout(restaurant_id, start_time, end_time, reason):
    path = get_slot_blackouts_csv_path()
    rows = _read(path, SLOT_BLACKOUT_HEADERS)
    blackout = {
        "id": csv_storage.next_int_id(rows),
        "restaurant_id": restaurant_id,
        "start_time": start_time,
        "end_time": end_time,
        "reason": reason,
    }
    csv_storage.append_row(path, SLOT_BLACKOUT_HEADERS, _blackout_to_row(blackout))
    return blackout


def get_blackouts_by_restaurant(restaurant_id):
    blackouts = []
    for row in _read(get_slot_blackouts_csv_path(), SLOT_BLACKOUT_HEADERS):
        blackout = _blackout_row_to_dict(row)
        if blackout["restaurant_id"] == restaurant_id:
            blackouts.append(blackout)
    return blackouts


def upsert_slot_booking(
    order_id,
    restaurant_id,
    slot_start,
    slot_end,
    status="scheduled",
):
    path = get_slot_bookings_csv_path()
    rows = _read(path, SLOT_BOOKING_HEADERS)

    for row in rows:
        if row["order_id"] == str(order_id):
            row["restaurant_id"] = str(restaurant_id)
            row["slot_start"] = slot_start
            row["slot_end"] = slot_end
            row["status"] = status
            _write(path, SLOT_BOOKING_HEADERS, rows)
            return _booking_row_to_dict(row)

    booking = {
        "id": csv_storage.next_int_id(rows),
        "order_id": str(order_id),
        "restaurant_id": restaurant_id,
        "slot_start": slot_start,
        "slot_end": slot_end,
        "status": status,
        "created_at": datetime.now().isoformat(),
    }
    csv_storage.append_row(path, SLOT_BOOKING_HEADERS, _booking_to_row(booking))
    return booking


def get_booking_by_order_id(order_id):
    for row in _read(get_slot_bookings_csv_path(), SLOT_BOOKING_HEADERS):
        booking = _booking_row_to_dict(row)
        if booking["order_id"] == str(order_id):
            return booking
    return None


def get_bookings_by_restaurant(restaurant_id):
    bookings = []
    for row in _read(get_slot_bookings_csv_path(), SLOT_BOOKING_HEADERS):
        booking = _booking_row_to_dict(row)
        if booking["restaurant_id"] == restaurant_id:
            bookings.append(booking)
    return bookings


def upsert_driver_assignment(order_id, driver_id):
    path = get_driver_assignments_csv_path()
    rows = _read(path, DRIVER_ASSIGNMENT_HEADERS)
    for row in rows:
        if row["order_id"] == str(order_id):
            row["driver_id"] = driver_id
            row["assigned_at"] = datetime.now().isoformat()
            _write(path, DRIVER_ASSIGNMENT_HEADERS, rows)
            return _assignment_row_to_dict(row)

    assignment = {
        "id": csv_storage.next_int_id(rows),
        "order_id": str(order_id),
        "driver_id": driver_id,
        "assigned_at": datetime.now().isoformat(),
    }
    csv_storage.append_row(path, DRIVER_ASSIGNMENT_HEADERS, _assignment_to_row(assignment))
    return assignment


def get_assignments_by_driver(driver_id):
    assignments = []
    for row in _read(get_driver_assignments_csv_path(), DRIVER_ASSIGNMENT_HEADERS):
        assignment = _assignment_row_to_dict(row)
        if assignment["driver_id"] == driver_id:
            assignments.append(assignment)
    return assignments


def clear():
    for path, headers in [
        (get_slot_configs_csv_path(), SLOT_CONFIG_HEADERS),
        (get_slot_blackouts_csv_path(), SLOT_BLACKOUT_HEADERS),
        (get_slot_bookings_csv_path(), SLOT_BOOKING_HEADERS),
        (get_driver_assignments_csv_path(), DRIVER_ASSIGNMENT_HEADERS),
    ]:
        _write(path, headers, [])
