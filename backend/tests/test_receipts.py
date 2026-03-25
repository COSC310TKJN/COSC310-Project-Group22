import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.repositories import payment_repo, receipt_repo

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_data():
    payment_repo.clear()
    receipt_repo.clear()
    yield
    payment_repo.clear()
    receipt_repo.clear()


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
