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


def test_receipt_generated_on_success():
    client.post("/payments/", json={
        "order_id": 50,
        "customer_id": "user_500",
        "amount": 100.00,
        "payment_method": "credit_card",
    })
    response = client.get("/payments/order/50/receipt")
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == 50
    assert data["amount"] == 100.00
    assert data["tax"] == 10.00
    assert data["total"] == 110.00
    assert data["receipt_number"].startswith("REC-")


def test_no_receipt_on_failure():
    client.post("/payments/", json={
        "order_id": 60,
        "customer_id": "user_600",
        "amount": 15000.00,
        "payment_method": "paypal",
    })
    response = client.get("/payments/order/60/receipt")
    assert response.status_code == 404


def test_get_receipt_by_order():
    client.post("/payments/", json={
        "order_id": 70,
        "customer_id": "user_700",
        "amount": 50.00,
        "payment_method": "debit_card",
    })
    response = client.get("/payments/order/70/receipt")
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == "user_700"
    assert data["payment_method"] == "debit_card"
