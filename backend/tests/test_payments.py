import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.roles import Role
from backend.app.main import app
from backend.app.database import Base, get_db
from backend.app.routes import auth_routes
from backend.app.user_storage import append_user, next_user_id
from backend.models.user import User
from backend.app.security import hash_password
from backend.repositories import payment_repo, receipt_repo

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
def clean_data():
    Base.metadata.create_all(bind=engine)
    payment_repo.clear()
    receipt_repo.clear()
    yield
    payment_repo.clear()
    receipt_repo.clear()
    auth_routes.clear_sessions()
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


def test_paid_order_validated():
    client.post("/payments/", json={
        "order_id": 30,
        "customer_id": "user_300",
        "amount": 50.00,
        "payment_method": "credit_card",
    })
    response = client.get("/payments/order/30/validate")
    assert response.status_code == 200
    data = response.json()
    assert data["is_paid"] is True


def test_unpaid_order_blocked():
    response = client.get("/payments/order/9999/validate")
    assert response.status_code == 200
    data = response.json()
    assert data["is_paid"] is False
    assert "No payment found" in data["message"]


def test_failed_payment_order_blocked():
    client.post("/payments/", json={
        "order_id": 40,
        "customer_id": "user_400",
        "amount": 15000.00,
        "payment_method": "paypal",
    })
    response = client.get("/payments/order/40/validate")
    assert response.status_code == 200
    data = response.json()
    assert data["is_paid"] is False
    assert "not completed" in data["message"].lower()


def test_manager_sees_paid_orders():
    client.post("/payments/", json={
        "order_id": 50,
        "customer_id": "user_500",
        "amount": 50.00,
        "payment_method": "credit_card",
    })
    client.post("/payments/", json={
        "order_id": 51,
        "customer_id": "user_501",
        "amount": 15000.00,
        "payment_method": "paypal",
    })
    db = TestingSessionLocal()
    try:
        manager = create_test_user(db, "manager_orders", "manager")
    finally:
        db.close()
    login_test_user("manager_orders")

    response = client.get(
        "/payments/manager/orders",
        headers={"X-User-Id": str(manager.id)},
    )
    assert response.status_code == 200
    orders = response.json()
    order_ids = [o["order_id"] for o in orders]
    assert 50 in order_ids
    assert 51 not in order_ids


def test_regular_user_blocked_from_paid_orders():
    db = TestingSessionLocal()
    try:
        regular_user = create_test_user(db, "regular_orders", "user")
    finally:
        db.close()
    login_test_user("regular_orders")

    response = client.get(
        "/payments/manager/orders",
        headers={"X-User-Id": str(regular_user.id)},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Manager role required."


def test_failed_payments_recorded():
    client.post("/payments/", json={
        "order_id": 60,
        "customer_id": "user_600",
        "amount": 15000.00,
        "payment_method": "credit_card",
    })
    db = TestingSessionLocal()
    try:
        manager = create_test_user(db, "manager_failed", "manager")
    finally:
        db.close()
    login_test_user("manager_failed")

    response = client.get(
        "/payments/manager/failed-payments",
        headers={"X-User-Id": str(manager.id)},
    )
    assert response.status_code == 200
    failed = response.json()
    assert len(failed) >= 1
    assert failed[0]["status"] == "failed"


def test_regular_user_blocked_from_failed_payments():
    db = TestingSessionLocal()
    try:
        regular_user = create_test_user(db, "regular_failed", "user")
    finally:
        db.close()
    login_test_user("regular_failed")

    response = client.get(
        "/payments/manager/failed-payments",
        headers={"X-User-Id": str(regular_user.id)},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Manager role required."


def test_no_failed_payments():
    db = TestingSessionLocal()
    try:
        manager = create_test_user(db, "manager_empty_failed", "manager")
    finally:
        db.close()
    login_test_user("manager_empty_failed")

    response = client.get(
        "/payments/manager/failed-payments",
        headers={"X-User-Id": str(manager.id)},
    )
    assert response.status_code == 200
    assert response.json() == []


def create_test_user(db, username, role):
    user = User(
        id=next_user_id(),
        username=username,
        hashed_password=hash_password("TestPass123"),
        role=role,
        is_manager=(role == Role.MANAGER),
    )
    append_user(user)
    return user


def login_test_user(username, password="TestPass123"):
    response = client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response.json()["id"]
