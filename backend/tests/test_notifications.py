import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base, get_db
from backend.app.main import app

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_notify_order_placed():
    response = client.post("/notifications/order-placed?user_id=user_1&order_id=100")
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == "user_1"
    assert data["notification_type"] == "order_placed"
    assert data["order_id"] == 100
    assert data["is_read"] is False
    assert "order #100" in data["message"]


def test_get_notifications():
    client.post("/notifications/order-placed?user_id=user_2&order_id=200")
    client.post("/notifications/order-placed?user_id=user_2&order_id=201")
    response = client.get("/notifications/?user_id=user_2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_unread_count():
    client.post("/notifications/order-placed?user_id=user_3&order_id=300")
    client.post("/notifications/order-placed?user_id=user_3&order_id=301")
    response = client.get("/notifications/unread/count?user_id=user_3")
    assert response.status_code == 200
    assert response.json()["unread_count"] == 2


def test_mark_as_read():
    create = client.post("/notifications/order-placed?user_id=user_4&order_id=400")
    notification_id = create.json()["id"]
    response = client.patch(f"/notifications/{notification_id}/read")
    assert response.status_code == 200
    assert response.json()["is_read"] is True
    count = client.get("/notifications/unread/count?user_id=user_4")
    assert count.json()["unread_count"] == 0


def test_notify_status_change():
    response = client.post("/notifications/status-change?user_id=user_5&order_id=500&new_status=preparing")
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == "user_5"
    assert data["notification_type"] == "status_change"
    assert data["order_id"] == 500
    assert "preparing" in data["message"]


def test_multiple_status_changes():
    client.post("/notifications/status-change?user_id=user_6&order_id=600&new_status=preparing")
    client.post("/notifications/status-change?user_id=user_6&order_id=600&new_status=out_for_delivery")
    response = client.get("/notifications/?user_id=user_6")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    messages = [n["message"] for n in data]
    assert any("preparing" in m for m in messages)
    assert any("out_for_delivery" in m for m in messages)


def test_delivery_notification():
    response = client.post("/notifications/delivery?user_id=user_7&order_id=700")
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == "user_7"
    assert data["notification_type"] == "delivery"
    assert data["order_id"] == 700
    assert "delivered" in data["message"].lower()


def test_manager_notified_new_order():
    response = client.post("/notifications/manager/new-order?manager_id=manager_1&order_id=800")
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == "manager_1"
    assert data["notification_type"] == "manager_new_order"
    assert data["order_id"] == 800
    assert "order #800" in data["message"]
    notifs = client.get("/notifications/?user_id=manager_1")
    assert len(notifs.json()) == 1


def test_cancellation_notification():
    response = client.post("/notifications/order-cancelled?user_id=user_8&order_id=900")
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == "user_8"
    assert data["notification_type"] == "order_cancelled"
    assert data["order_id"] == 900
    assert "cancelled" in data["message"]
    count = client.get("/notifications/unread/count?user_id=user_8")
    assert count.json()["unread_count"] == 1


def test_set_notification_preferences():
    response = client.put("/notifications/preferences?user_id=user_9&notification_type=order_placed&enabled=true&channel=email")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user_9"
    assert data["notification_type"] == "order_placed"
    assert data["enabled"] is True
    assert data["channel"] == "email"


def test_get_preferences():
    client.put("/notifications/preferences?user_id=user_10&notification_type=order_placed&enabled=true&channel=sms")
    client.put("/notifications/preferences?user_id=user_10&notification_type=delivery&enabled=false&channel=in_app")
    response = client.get("/notifications/preferences?user_id=user_10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_disabled_notification_not_sent():
    client.put("/notifications/preferences?user_id=user_11&notification_type=order_placed&enabled=false")
    client.post("/notifications/order-placed?user_id=user_11&order_id=1100")
    notifs = client.get("/notifications/?user_id=user_11")
    assert len(notifs.json()) == 0


def test_enabled_notification_sent():
    client.put("/notifications/preferences?user_id=user_12&notification_type=order_placed&enabled=true&channel=email")
    client.post("/notifications/order-placed?user_id=user_12&order_id=1200")
    notifs = client.get("/notifications/?user_id=user_12")
    assert len(notifs.json()) == 1
    assert notifs.json()[0]["channel"] == "email"
