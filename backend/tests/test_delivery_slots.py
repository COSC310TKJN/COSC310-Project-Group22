import os

os.environ.setdefault("SKIP_RESTAURANT_BOOTSTRAP", "1")

import pytest
from fastapi.testclient import TestClient

from backend.app import auth_session
from backend.app.main import app
from backend.app.restaurant_storage import (
    RestaurantRecord,
    append_restaurant,
    ensure_restaurants_csv_exists,
)
from backend.repositories import delivery_slot_repo, order_repo
from backend.services.order_service import orders_db as service_orders_db


@pytest.fixture(autouse=True)
def isolated_delivery_slot_data(monkeypatch, tmp_path):
    monkeypatch.setenv("RESTAURANTS_CSV_PATH", str(tmp_path / "restaurants.csv"))
    monkeypatch.setenv("AUTH_USERS_CSV_PATH", str(tmp_path / "users.csv"))
    monkeypatch.setenv("ORDERS_CSV_PATH", str(tmp_path / "orders.csv"))
    monkeypatch.setenv(
        "DELIVERY_STATUS_UPDATES_CSV_PATH",
        str(tmp_path / "delivery_status_updates.csv"),
    )
    monkeypatch.setenv(
        "DELIVERY_SLOT_CONFIGS_CSV_PATH",
        str(tmp_path / "delivery_slot_configs.csv"),
    )
    monkeypatch.setenv(
        "DELIVERY_SLOT_BLACKOUTS_CSV_PATH",
        str(tmp_path / "delivery_slot_blackouts.csv"),
    )
    monkeypatch.setenv(
        "DELIVERY_SLOT_BOOKINGS_CSV_PATH",
        str(tmp_path / "delivery_slot_bookings.csv"),
    )
    monkeypatch.setenv(
        "DELIVERY_SLOT_DRIVER_ASSIGNMENTS_CSV_PATH",
        str(tmp_path / "delivery_slot_driver_assignments.csv"),
    )

    ensure_restaurants_csv_exists()
    append_restaurant(
        RestaurantRecord(
            id=1,
            name="Test Restaurant",
            cuisine_type="American",
            address="111 Test Ave",
        )
    )

    order_repo.orders_db.clear()
    service_orders_db.clear()
    delivery_slot_repo.clear()
    auth_session.clear_sessions()
    yield
    order_repo.orders_db.clear()
    service_orders_db.clear()
    delivery_slot_repo.clear()
    auth_session.clear_sessions()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def _login_manager(client, username="slot_manager"):
    register_response = client.post(
        "/auth/register",
        json={"username": username, "password": "Manager123", "role": "manager"},
    )
    assert register_response.status_code == 201
    login_response = client.post(
        "/auth/login",
        json={"username": username, "password": "Manager123"},
    )
    assert login_response.status_code == 200
    return login_response.json()["id"]


def _create_order(client, customer_id):
    response = client.post(
        "/orders/",
        json={
            "restaurant_id": 1,
            "food_item": "Pizza",
            "order_value": 20,
            "customer_id": customer_id,
        },
    )
    assert response.status_code == 201
    return str(response.json()["id"])


def test_select_slot(client):
    availability = client.get(
        "/restaurants/1/delivery-slots/availability",
        params={"date": "2026-04-07"},
    )
    assert availability.status_code == 200
    slots = availability.json()["slots"]
    assert len(slots) > 0
    selected_slot = slots[0]["slot_start"]

    order_id = _create_order(client, customer_id="C1")
    booking = client.post(
        f"/orders/{order_id}/delivery-slot",
        json={"slot_start": selected_slot},
    )
    assert booking.status_code == 201
    booking_data = booking.json()
    assert booking_data["order_id"] == order_id
    assert booking_data["slot_start"] == selected_slot
    assert booking_data["status"] == "scheduled"


def test_slot_capacity(client):
    manager_id = _login_manager(client, username="cap_manager")
    config = client.put(
        "/admin/restaurants/1/delivery-slot-config",
        json={"slot_duration_minutes": 60, "slot_capacity": 1},
        headers={"X-User-Id": str(manager_id)},
    )
    assert config.status_code == 200

    availability = client.get(
        "/restaurants/1/delivery-slots/availability",
        params={"date": "2026-04-07"},
    )
    slot_start = availability.json()["slots"][0]["slot_start"]

    first_order = _create_order(client, customer_id="C2")
    second_order = _create_order(client, customer_id="C3")

    first_booking = client.post(
        f"/orders/{first_order}/delivery-slot",
        json={"slot_start": slot_start},
    )
    assert first_booking.status_code == 201

    second_booking = client.post(
        f"/orders/{second_order}/delivery-slot",
        json={"slot_start": slot_start},
    )
    assert second_booking.status_code == 409
    assert "unavailable" in second_booking.json()["detail"].lower()

    refreshed_availability = client.get(
        "/restaurants/1/delivery-slots/availability",
        params={"date": "2026-04-07"},
    )
    target_slot = next(
        s for s in refreshed_availability.json()["slots"] if s["slot_start"] == slot_start
    )
    assert target_slot["is_available"] is False
    assert target_slot["disabled_reason"] == "full"


def test_blackout_slots(client):
    manager_id = _login_manager(client, username="blackout_manager")
    blackout_create = client.post(
        "/admin/restaurants/1/delivery-blackouts",
        json={
            "start_time": "2026-04-07T10:00:00+00:00",
            "end_time": "2026-04-07T12:00:00+00:00",
            "reason": "Kitchen maintenance",
        },
        headers={"X-User-Id": str(manager_id)},
    )
    assert blackout_create.status_code == 201

    availability = client.get(
        "/restaurants/1/delivery-slots/availability",
        params={"date": "2026-04-07"},
    )
    assert availability.status_code == 200
    first_two_slots = availability.json()["slots"][:2]
    assert all(slot["is_available"] is False for slot in first_two_slots)
    assert all(slot["disabled_reason"] == "blackout" for slot in first_two_slots)


def test_manager_admin_controls(client):
    unauth_config = client.put(
        "/admin/restaurants/1/delivery-slot-config",
        json={"slot_duration_minutes": 45, "slot_capacity": 4},
    )
    assert unauth_config.status_code == 401

    user_register = client.post(
        "/auth/register",
        json={"username": "regular_user", "password": "UserPass123", "role": "user"},
    )
    assert user_register.status_code == 201
    user_login = client.post(
        "/auth/login",
        json={"username": "regular_user", "password": "UserPass123"},
    )
    assert user_login.status_code == 200
    forbidden_config = client.put(
        "/admin/restaurants/1/delivery-slot-config",
        json={"slot_duration_minutes": 45, "slot_capacity": 4},
        headers={"X-User-Id": str(user_login.json()["id"])},
    )
    assert forbidden_config.status_code == 403

    manager_id = _login_manager(client, username="admin_ok")
    manager_config = client.put(
        "/admin/restaurants/1/delivery-slot-config",
        json={"slot_duration_minutes": 45, "slot_capacity": 4},
        headers={"X-User-Id": str(manager_id)},
    )
    assert manager_config.status_code == 200
    assert manager_config.json()["slot_duration_minutes"] == 45
    assert manager_config.json()["slot_capacity"] == 4

    manager_blackout = client.post(
        "/admin/restaurants/1/delivery-blackouts",
        json={
            "start_time": "2026-04-10T14:00:00+00:00",
            "end_time": "2026-04-10T15:30:00+00:00",
            "reason": "Private event",
        },
        headers={"X-User-Id": str(manager_id)},
    )
    assert manager_blackout.status_code == 201

    list_blackouts = client.get(
        "/admin/restaurants/1/delivery-blackouts",
        params={"date": "2026-04-10"},
        headers={"X-User-Id": str(manager_id)},
    )
    assert list_blackouts.status_code == 200
    assert len(list_blackouts.json()) == 1


def test_driver_queue(client):
    availability = client.get(
        "/restaurants/1/delivery-slots/availability",
        params={"date": "2026-04-12"},
    )
    slots = availability.json()["slots"]
    early_slot = slots[0]["slot_start"]
    later_slot = slots[2]["slot_start"]

    first_order = _create_order(client, customer_id="C8")
    second_order = _create_order(client, customer_id="C9")

    first_booking = client.post(
        f"/orders/{first_order}/delivery-slot",
        json={"slot_start": early_slot},
    )
    second_booking = client.post(
        f"/orders/{second_order}/delivery-slot",
        json={"slot_start": later_slot},
    )
    assert first_booking.status_code == 201
    assert second_booking.status_code == 201

    unauthorized_assignment = client.post(
        "/delivery-slots/assignments",
        json={"order_id": first_order, "driver_id": "driver_1"},
    )
    assert unauthorized_assignment.status_code == 403

    assign_1 = client.post(
        "/delivery-slots/assignments",
        json={"order_id": first_order, "driver_id": "driver_1"},
        headers={"X-Role": "driver"},
    )
    assign_2 = client.post(
        "/delivery-slots/assignments",
        json={"order_id": second_order, "driver_id": "driver_1"},
        headers={"X-Role": "driver"},
    )
    assert assign_1.status_code == 201
    assert assign_2.status_code == 201

    queue = client.get(
        "/drivers/driver_1/delivery-queue",
        params={"date": "2026-04-12"},
    )
    assert queue.status_code == 200
    items = queue.json()["items"]
    assert len(items) == 2
    assert items[0]["slot_start"] == early_slot
    assert items[1]["slot_start"] == later_slot
