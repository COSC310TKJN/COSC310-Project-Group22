import os

os.environ.setdefault("SKIP_RESTAURANT_BOOTSTRAP", "1")

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.restaurant_storage import RestaurantRecord, append_restaurant, ensure_restaurants_csv_exists


@pytest.fixture
def client_with_restaurants(monkeypatch, tmp_path):
    csv_path = tmp_path/ "restaurants.csv"
    monkeypatch.setenv("RESTAURANTS_CSV_PATH", str(csv_path))
    ensure_restaurants_csv_exists()
    append_restaurant(
        RestaurantRecord(id=1, name="Restaurant 1", cuisine_type="American", address="City 1")
    )
    append_restaurant(
        RestaurantRecord(id=2, name="Restaurant 2", cuisine_type="Asian", address="City 2")
    )
    with TestClient(app) as client:
        yield client


def test_browse_restaurants(client_with_restaurants):
    response = client_with_restaurants.get("/restaurants/?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert len(data["items"]) >= 2
    assert data["page"] == 1
    assert data["page_size"] == 10


def test_filter_by_cuisine(client_with_restaurants):
    response = client_with_restaurants.get("/restaurants/?cuisine=American")
    assert response.status_code == 200
    data = response.json()
    assert all(item["cuisine_type"] == "American" for item in data["items"])


def test_search_restaurants_by_name(client_with_restaurants):
    response = client_with_restaurants.get("/restaurants/search?q=Restaurant%201")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(item["id"] == 1 for item in data["items"])


def test_get_restaurant_menu_unique(client_with_restaurants):
    r1 = client_with_restaurants.get("/restaurants/1/menu").json()
    r2 = client_with_restaurants.get("/restaurants/2/menu").json()
    names_1 = {item["name"] for item in r1}
    names_2 = {item["name"] for item in r2}
    assert "Taccos" in names_1
    assert "Taccos" not in names_2


def test_item_shows_computed_price(client_with_restaurants):
    response = client_with_restaurants.get("/restaurants/1/menu")
    assert response.status_code == 200
    data = response.json()
    for item in data:
        assert "estimated_price" in item
        assert item["estimated_price"] > 0


def test_get_restaurant_detail(client_with_restaurants):
    response = client_with_restaurants.get("/restaurants/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Restaurant 1"
    assert data["cuisine_type"] == "American"
    assert "menu_items" in data
    assert len(data["menu_items"]) == 8


def test_restaurant_not_found(client_with_restaurants):
    response = client_with_restaurants.get("/restaurants/99999")
    assert response.status_code == 404
