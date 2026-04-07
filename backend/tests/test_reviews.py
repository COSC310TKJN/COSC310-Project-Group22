import os
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.repositories import review_repo

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_data(tmp_path):
    os.environ["REVIEWS_CSV_PATH"] = str(tmp_path / "reviews.csv")
    review_repo.clear()
    yield
    review_repo.clear()


def _create_review(**overrides):
    payload = {
        "customer_id": "user_1",
        "order_id": 1,
        "restaurant_id": 10,
        "rating": 4,
        "comment": "Great food!",
    }
    payload.update(overrides)
    return client.post("/reviews/", json=payload)


def test_create_review():
    response = _create_review()
    assert response.status_code == 201
    data = response.json()
    assert data["customer_id"] == "user_1"
    assert data["order_id"] == 1
    assert data["restaurant_id"] == 10
    assert data["rating"] == 4
    assert data["comment"] == "Great food!"
    assert "id" in data
    assert "created_at" in data


def test_create_review_without_comment():
    response = _create_review(comment=None)
    assert response.status_code == 201
    assert response.json()["comment"] is None


def test_duplicate_review_rejected():
    _create_review(order_id=5, customer_id="user_dup")
    response = _create_review(order_id=5, customer_id="user_dup")
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_same_order_different_customer_allowed():
    _create_review(order_id=5, customer_id="user_a")
    response = _create_review(order_id=5, customer_id="user_b")
    assert response.status_code == 201


def test_rating_below_1_rejected():
    response = _create_review(rating=0)
    assert response.status_code == 422


def test_rating_above_5_rejected():
    response = _create_review(rating=6)
    assert response.status_code == 422


def test_get_review_by_id():
    create = _create_review()
    review_id = create.json()["id"]
    response = client.get(f"/reviews/{review_id}")
    assert response.status_code == 200
    assert response.json()["rating"] == 4


def test_get_review_not_found():
    response = client.get("/reviews/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_restaurant_reviews():
    _create_review(order_id=1, customer_id="user_a", restaurant_id=20, rating=5)
    _create_review(order_id=2, customer_id="user_b", restaurant_id=20, rating=3)
    _create_review(order_id=3, customer_id="user_c", restaurant_id=99, rating=1)

    response = client.get("/reviews/restaurant/20")
    assert response.status_code == 200
    reviews = response.json()
    assert len(reviews) == 2
    assert all(r["restaurant_id"] == 20 for r in reviews)


def test_get_restaurant_reviews_empty():
    response = client.get("/reviews/restaurant/9999")
    assert response.status_code == 200
    assert response.json() == []


def test_restaurant_average_rating():
    _create_review(order_id=1, customer_id="user_a", restaurant_id=30, rating=5)
    _create_review(order_id=2, customer_id="user_b", restaurant_id=30, rating=3)
    _create_review(order_id=3, customer_id="user_c", restaurant_id=30, rating=4)

    response = client.get("/reviews/restaurant/30/average")
    assert response.status_code == 200
    data = response.json()
    assert data["restaurant_id"] == 30
    assert data["average_rating"] == 4.0
    assert data["total_reviews"] == 3


def test_restaurant_average_rating_no_reviews():
    response = client.get("/reviews/restaurant/9999/average")
    assert response.status_code == 200
    data = response.json()
    assert data["average_rating"] == 0.0
    assert data["total_reviews"] == 0


def test_get_customer_reviews():
    _create_review(order_id=1, customer_id="user_x", restaurant_id=10)
    _create_review(order_id=2, customer_id="user_x", restaurant_id=20)
    _create_review(order_id=3, customer_id="user_y", restaurant_id=10)

    response = client.get("/reviews/customer/user_x")
    assert response.status_code == 200
    reviews = response.json()
    assert len(reviews) == 2
    assert all(r["customer_id"] == "user_x" for r in reviews)


def test_get_customer_reviews_empty():
    response = client.get("/reviews/customer/nobody")
    assert response.status_code == 200
    assert response.json() == []
