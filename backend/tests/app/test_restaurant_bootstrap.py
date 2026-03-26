import csv

from backend.app.bootstrap import check_restaurants_exist
from backend.app.restaurant_storage import (
    RESTAURANT_HEADERS,
    RestaurantRecord,
    append_restaurant,
    ensure_restaurants_csv_exists,
    load_restaurants,
    next_restaurant_id,
)
from backend.schemas.restaurant_schema import RestaurantResponse


def test_bootstrap_creates_restaurants_csv_with_headers(monkeypatch, tmp_path):
    restaurants_csv_path = tmp_path / "restaurants.csv"
    monkeypatch.delenv("SKIP_RESTAURANT_BOOTSTRAP", raising=False)
    monkeypatch.setenv("RESTAURANTS_CSV_PATH", str(restaurants_csv_path))

    check_restaurants_exist()

    with restaurants_csv_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        assert next(reader) == RESTAURANT_HEADERS


def test_bootstrap_seeds_restaurants_when_csv_is_empty(monkeypatch, tmp_path):
    restaurants_csv_path = tmp_path / "restaurants.csv"
    monkeypatch.delenv("SKIP_RESTAURANT_BOOTSTRAP", raising=False)
    monkeypatch.setenv("RESTAURANTS_CSV_PATH", str(restaurants_csv_path))

    ensure_restaurants_csv_exists()
    check_restaurants_exist()

    restaurants = load_restaurants()

    assert len(restaurants) == 100
    assert restaurants[0] == RestaurantRecord(
        id=1,
        name="Restaurant 1",
        cuisine_type="American",
        address="City 2, Street 1",
    )


def test_bootstrap_does_not_duplicate_seeded_restaurants(monkeypatch, tmp_path):
    restaurants_csv_path = tmp_path / "restaurants.csv"
    monkeypatch.delenv("SKIP_RESTAURANT_BOOTSTRAP", raising=False)
    monkeypatch.setenv("RESTAURANTS_CSV_PATH", str(restaurants_csv_path))

    check_restaurants_exist()
    check_restaurants_exist()

    restaurants = load_restaurants()

    assert len(restaurants) == 100
    assert restaurants[-1].id == 100


def test_loaded_restaurant_matches_response_schema(monkeypatch, tmp_path):
    restaurants_csv_path = tmp_path / "restaurants.csv"
    monkeypatch.setenv("RESTAURANTS_CSV_PATH", str(restaurants_csv_path))

    append_restaurant(
        RestaurantRecord(
            id=7,
            name="Campus Kitchen",
            cuisine_type="American",
            address="Kelowna Campus",
        )
    )

    restaurant = load_restaurants()[0]
    response = RestaurantResponse.model_validate(restaurant)

    assert response.id == 7
    assert response.name == "Campus Kitchen"
    assert response.cuisine_type == "American"
    assert response.address == "Kelowna Campus"


def test_restaurant_data_persists_and_next_id_advances(monkeypatch, tmp_path):
    restaurants_csv_path = tmp_path / "restaurants.csv"
    monkeypatch.setenv("RESTAURANTS_CSV_PATH", str(restaurants_csv_path))

    append_restaurant(
        RestaurantRecord(
            id=3,
            name="Pizza Lab",
            cuisine_type="Italian",
            address="Science Building",
        )
    )

    restaurants = load_restaurants()

    assert restaurants == [
        RestaurantRecord(
            id=3,
            name="Pizza Lab",
            cuisine_type="Italian",
            address="Science Building",
        )
    ]
    assert next_restaurant_id() == 4
