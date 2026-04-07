import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.models.order import OrderStatus
from backend.repositories.order_repo import orders_db
from backend.services.order_service import reorder_drafts

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_data():
    orders_db.clear()
    reorder_drafts.clear()
    yield
    orders_db.clear()
    reorder_drafts.clear()


def create_delivered_order(order_id: str, customer_id: str = "C1", order_time: str = "2025-03-11T12:00:00"):
    response = client.post(
        "/orders",
        json={
            "order_id": order_id,
            "restaurant_id": 10,
            "food_item": "Pizza",
            "order_time": order_time,
            "order_value": 20,
            "delivery_method": "bike",
            "delivery_distance": 5,
            "customer_id": customer_id,
        },
    )
    assert response.status_code == 200
    orders_db[order_id].status = OrderStatus.DELIVERED


def test_create_reorder_draft_success():
    create_delivered_order("100", customer_id="C100")

    response = client.post("/orders/100/reorder", json={"customer_id": "C100"})

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Reorder draft created"
    assert data["reorder_draft_id"]
    assert data["order"]["source_order_id"] == "100"


def test_create_reorder_draft_not_found():
    response = client.post("/orders/999/reorder", json={"customer_id": "C1"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_create_reorder_draft_requires_delivered_order():
    client.post(
        "/orders",
        json={
            "order_id": "101",
            "restaurant_id": 10,
            "food_item": "Burger",
            "order_time": "2025-03-11T12:00:00",
            "order_value": 12,
            "delivery_method": "car",
            "delivery_distance": 2,
            "customer_id": "C101",
        },
    )
    response = client.post("/orders/101/reorder", json={"customer_id": "C101"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Only delivered orders can be reordered"


def test_create_reorder_draft_rejects_customer_mismatch():
    create_delivered_order("102", customer_id="C102")

    response = client.post("/orders/102/reorder", json={"customer_id": "OTHER"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Cannot reorder another customer's order"


def test_update_reorder_draft_success():
    create_delivered_order("103", customer_id="C103")
    draft = client.post("/orders/103/reorder", json={"customer_id": "C103"})
    draft_id = draft.json()["reorder_draft_id"]

    response = client.patch(
        f"/orders/reorder/{draft_id}",
        json={"order_time": "2026-01-01T10:00:00", "delivery_method": "car"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["order"]["order_time"] == "2026-01-01T10:00:00"
    assert data["order"]["delivery_method"] == "car"


def test_update_reorder_draft_not_found():
    response = client.patch(
        "/orders/reorder/unknown-draft",
        json={"order_time": "2026-01-01T10:00:00"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Reorder draft not found"


def test_update_reorder_draft_rejects_disallowed_fields():
    create_delivered_order("104", customer_id="C104")
    draft = client.post("/orders/104/reorder", json={"customer_id": "C104"})
    draft_id = draft.json()["reorder_draft_id"]

    response = client.patch(
        f"/orders/reorder/{draft_id}",
        json={"food_item": "Sushi"},
    )
    assert response.status_code == 400
    assert "Only order_time, delivery_method, and delivery_distance" in response.json()["detail"]


def test_confirm_reorder_success_creates_new_order():
    create_delivered_order("105", customer_id="C105")
    source_snapshot = orders_db["105"].to_dict().copy()
    draft = client.post("/orders/105/reorder", json={"customer_id": "C105"})
    draft_id = draft.json()["reorder_draft_id"]

    response = client.post(f"/orders/reorder/{draft_id}/confirm")

    assert response.status_code == 200
    data = response.json()["order"]
    assert data["order_id"] != "105"
    assert data["source_order_id"] == "105"
    assert data["customer_id"] == "C105"
    assert orders_db["105"].to_dict() == source_snapshot


def test_confirm_reorder_not_found():
    response = client.post("/orders/reorder/unknown-draft/confirm")
    assert response.status_code == 404
    assert response.json()["detail"] == "Reorder draft not found"


def test_order_history_includes_original_and_reorder():
    create_delivered_order("106", customer_id="C106", order_time="2025-01-01T10:00:00")
    draft = client.post("/orders/106/reorder", json={"customer_id": "C106"})
    draft_id = draft.json()["reorder_draft_id"]
    client.patch(
        f"/orders/reorder/{draft_id}",
        json={"order_time": "2026-01-01T10:00:00"},
    )
    confirm = client.post(f"/orders/reorder/{draft_id}/confirm")
    new_order_id = confirm.json()["order"]["order_id"]

    response = client.get("/orders/history/C106")

    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == "C106"
    assert len(data["orders"]) == 2
    assert data["orders"][0]["order_id"] == new_order_id
    assert data["orders"][0]["source_order_id"] == "106"
    assert data["orders"][1]["order_id"] == "106"


def test_order_history_empty_for_customer_with_no_orders():
    response = client.get("/orders/history/NO_ORDERS")
    assert response.status_code == 200
    assert response.json()["orders"] == []
