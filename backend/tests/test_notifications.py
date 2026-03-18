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
