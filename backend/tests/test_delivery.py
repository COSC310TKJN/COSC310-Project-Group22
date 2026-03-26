import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture(autouse=True)
def delivery_csv_isolated(monkeypatch, tmp_path):
    orders_path = tmp_path / "delivery_orders.csv"
    status_path = tmp_path / "delivery_status_updates.csv"
    monkeypatch.setenv("DELIVERY_ORDERS_CSV_PATH", str(orders_path))
    monkeypatch.setenv("DELIVERY_STATUS_UPDATES_CSV_PATH", str(status_path))


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_create_order_and_get_status(client):
    r = client.post("/orders/", json={"customer_id": "C1", "food_item": "Pizza"})
    assert r.status_code == 201
    order_id = r.json()["id"]
    r = client.get(f"/orders/{order_id}/status")
    assert r.status_code == 200
    assert r.json()["current_status"] == "created"
    assert r.json()["order_id"] == order_id


def test_tracking_includes_timestamps(client):
    r = client.post("/orders/", json={"customer_id": "C2"})
    assert r.status_code == 201
    order_id = r.json()["id"]
    r = client.get(f"/orders/{order_id}/tracking")
    assert r.status_code == 200
    history = r.json()["status_history"]
    assert len(history) >= 1
    assert history[0]["status"] == "created"
    assert "updated_at" in history[0]


def test_authorized_role_can_update_status(client):
    r = client.post("/orders/", json={"customer_id": "C3"})
    order_id = r.json()["id"]
    r = client.patch(
        f"/orders/{order_id}/status",
        json={"new_status": "paid"},
        headers={"X-Role": "admin"},
    )
    assert r.status_code == 200
    assert r.json()["new_status"] == "paid"
    assert r.json()["previous_status"] == "created"


def test_reject_unauthorized_update(client):
    r = client.post("/orders/", json={"customer_id": "C4"})
    order_id = r.json()["id"]
    r = client.patch(
        f"/orders/{order_id}/status",
        json={"new_status": "paid"},
        headers={"X-Role": "customer"},
    )
    assert r.status_code == 403
    r = client.patch(
        f"/orders/{order_id}/status",
        json={"new_status": "paid"},
    )
    assert r.status_code == 403


def test_lock_delivered_order(client):
    r = client.post("/orders/", json={"customer_id": "C5"})
    order_id = r.json()["id"]
    for status in ["paid", "preparing", "out_for_delivery", "delivered"]:
        r = client.patch(
            f"/orders/{order_id}/status",
            json={"new_status": status},
            headers={"X-Role": "driver"},
        )
        assert r.status_code == 200, r.json()
    r = client.patch(
        f"/orders/{order_id}/status",
        json={"new_status": "preparing"},
        headers={"X-Role": "admin"},
    )
    assert r.status_code == 400
    assert "Delivered" in r.json()["detail"] or "delivered" in r.json()["detail"].lower()
