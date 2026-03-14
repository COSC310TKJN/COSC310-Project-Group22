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


def test_successful_payment():
    response = client.post("/payments/", json={
        "order_id": 1,
        "customer_id": "user_123",
        "amount": 29.99,
        "payment_method": "credit_card",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "completed"
    assert data["order_id"] == 1
    assert data["amount"] == 29.99
    assert data["payment_method"] == "credit_card"
    assert "transaction_id" in data


def test_failed_payment():
    response = client.post("/payments/", json={
        "order_id": 2,
        "customer_id": "user_456",
        "amount": 15000.00,
        "payment_method": "paypal",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "failed"


def test_duplicate_payment():
    client.post("/payments/", json={
        "order_id": 3,
        "customer_id": "user_789",
        "amount": 50.00,
        "payment_method": "debit_card",
    })
    response = client.post("/payments/", json={
        "order_id": 3,
        "customer_id": "user_789",
        "amount": 50.00,
        "payment_method": "debit_card",
    })
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_get_payment_status():
    create = client.post("/payments/", json={
        "order_id": 10,
        "customer_id": "user_100",
        "amount": 25.00,
        "payment_method": "credit_card",
    })
    payment_id = create.json()["id"]
    response = client.get(f"/payments/{payment_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == 10
    assert data["status"] == "completed"


def test_get_payment_not_found():
    response = client.get("/payments/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_payment_by_order():
    client.post("/payments/", json={
        "order_id": 20,
        "customer_id": "user_200",
        "amount": 40.00,
        "payment_method": "paypal",
    })
    response = client.get("/payments/order/20")
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == 20
    assert data["status"] == "completed"


def test_get_payment_by_order_not_found():
    response = client.get("/payments/order/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_payment_methods():
    response = client.get("/payments/methods")
    assert response.status_code == 200
    methods = response.json()
    assert len(methods) == 3
    names = [m["name"] for m in methods]
    assert "credit_card" in names
    assert "debit_card" in names
    assert "paypal" in names
