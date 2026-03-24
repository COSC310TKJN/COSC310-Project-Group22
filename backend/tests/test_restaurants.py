import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base, get_db
from backend.app.main import app
from backend.models.restaurant import Restaurant

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
    db = TestingSessionLocal()
    try:
        db.add(Restaurant(id=1, name="Restaurant 1", cuisine_type="American", address="City 1"))
        db.add(Restaurant(id=2, name="Restaurant 2", cuisine_type="Asian", address="City 2"))
        db.commit()
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def test_browse_restaurants():
    response = client.get("/restaurants/?page=1&page_size=10")
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


def test_get_restaurant_menu_unique():
    r1 = client.get("/restaurants/1/menu").json()
    r2 = client.get("/restaurants/2/menu").json()
    names_1 = {item["name"] for item in r1}
    names_2 = {item["name"] for item in r2}
    assert "Taccos" in names_1
    assert "Taccos" not in names_2


def test_item_shows_computed_price():
    response = client.get("/restaurants/1/menu")
    assert response.status_code == 200
    data = response.json()
    for item in data:
        assert "estimated_price" in item
        assert item["estimated_price"] > 0


def test_get_restaurant_detail():
    response = client.get("/restaurants/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Restaurant 1"
    assert data["cuisine_type"] == "American"
    assert "menu_items" in data
    assert len(data["menu_items"]) == 8


def test_restaurant_not_found():
    response = client.get("/restaurants/99999")
    assert response.status_code == 404
