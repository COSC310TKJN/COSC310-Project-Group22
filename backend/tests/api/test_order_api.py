import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.repositories.order_repo import orders_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_data():
    orders_db.clear()
    yield
    orders_db.clear()


def test_create_order_api():
    response = client.post("/orders", json={
        "order_id": "1",
        "restaurant_id": 10,
        "food_item": "Pizza",
        "order_time": "2025-03-11T12:00:00",
        "order_value": 20,
        "delivery_method": "bike",
        "delivery_distance": 5,
        "customer_id": "C1"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Order created"


def test_get_order_api():
    client.post("/orders", json={
        "order_id": "2",
        "restaurant_id": 10,
        "food_item": "Burger",
        "order_time": "2025-03-11T12:00:00",
        "order_value": 15,
        "delivery_method": "car",
        "delivery_distance": 3,
        "customer_id": "C2"
    })
    
    response = client.get("/orders/2")
    assert response.status_code == 200
    assert response.json()["order_id"] == "2"


def test_cancel_order_api():
    client.post("/orders", json={
        "order_id": "3",
        "restaurant_id": 10,
        "food_item": "Sushi",
        "order_time": "2025-03-11T12:00:00",
        "order_value": 30,
        "delivery_method": "bike",
        "delivery_distance": 6,
        "customer_id": "C3"
    })
    
    response = client.post("/orders/3/cancel")
    assert response.status_code == 200
    assert response.json()["message"] == "Order cancelled"


def test_get_order_not_found_api():
    response = client.get("/orders/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_invalid_customer_api():
    response = client.post("/orders", json={
        "order_id": "4",
        "restaurant_id": 10,
        "food_item": "Pizza",
        "order_time": "2025-03-11T12:00:00",
        "order_value": 20,
        "delivery_method": "bike",
        "delivery_distance": 5,
        "customer_id": "INVALID"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Customer is not eligible"


def test_get_order_total_api():
    client.post("/orders", json={
        "order_id": "5",
        "restaurant_id": 10,
        "food_item": "Pizza",
        "order_time": "2025-03-11T12:00:00",
        "order_value": 20,
        "delivery_method": "bike",
        "delivery_distance": 5,
        "customer_id": "C5"
    })
    
    response = client.get("/orders/5/total")
    assert response.status_code == 200
    assert response.json()["order_id"] == "5"