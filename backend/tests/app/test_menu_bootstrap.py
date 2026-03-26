import csv

import pytest

from backend.app.bootstrap import check_menu_items_exist, check_restaurants_exist
from backend.app.menu_storage import (
    MENU_ITEM_HEADERS,
    MenuItemRecord,
    append_menu_item,
    ensure_menu_items_csv_exists,
    load_menu_items,
    load_menu_items_for_restaurant,
    next_menu_item_id,
)
from backend.schemas.restaurant_schema import MenuItemResponse


def test_menu_bootstrap_creates_csv_with_headers(monkeypatch, tmp_path):
    restaurants_csv_path = tmp_path / "restaurants.csv"
    menu_items_csv_path = tmp_path / "menu_items.csv"
    monkeypatch.delenv("SKIP_RESTAURANT_BOOTSTRAP", raising=False)
    monkeypatch.setenv("RESTAURANTS_CSV_PATH", str(restaurants_csv_path))
    monkeypatch.setenv("MENU_ITEMS_CSV_PATH", str(menu_items_csv_path))

    check_restaurants_exist()
    check_menu_items_exist()

    with menu_items_csv_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        assert next(reader) == MENU_ITEM_HEADERS


def test_menu_bootstrap_seeds_items_for_restaurants(monkeypatch, tmp_path):
    restaurants_csv_path = tmp_path / "restaurants.csv"
    menu_items_csv_path = tmp_path / "menu_items.csv"
    monkeypatch.delenv("SKIP_RESTAURANT_BOOTSTRAP", raising=False)
    monkeypatch.setenv("RESTAURANTS_CSV_PATH", str(restaurants_csv_path))
    monkeypatch.setenv("MENU_ITEMS_CSV_PATH", str(menu_items_csv_path))

    check_restaurants_exist()
    ensure_menu_items_csv_exists()
    check_menu_items_exist()

    menu_items = load_menu_items()

    assert len(menu_items) == 800
    assert all(item.restaurant_id >= 1 for item in menu_items)
    assert len(load_menu_items_for_restaurant(1)) == 8


def test_menu_bootstrap_does_not_duplicate_seeded_items(monkeypatch, tmp_path):
    restaurants_csv_path = tmp_path / "restaurants.csv"
    menu_items_csv_path = tmp_path / "menu_items.csv"
    monkeypatch.delenv("SKIP_RESTAURANT_BOOTSTRAP", raising=False)
    monkeypatch.setenv("RESTAURANTS_CSV_PATH", str(restaurants_csv_path))
    monkeypatch.setenv("MENU_ITEMS_CSV_PATH", str(menu_items_csv_path))

    check_restaurants_exist()
    check_menu_items_exist()
    check_menu_items_exist()

    assert len(load_menu_items()) == 800


def test_loaded_menu_item_matches_response_schema(monkeypatch, tmp_path):
    menu_items_csv_path = tmp_path / "menu_items.csv"
    monkeypatch.setenv("MENU_ITEMS_CSV_PATH", str(menu_items_csv_path))

    append_menu_item(
        MenuItemRecord(
            id=12,
            restaurant_id=5,
            name="Test Pasta",
            base_price=14.5,
            estimated_price=14.5,
            description="Fresh pasta",
            category="Entree",
        )
    )

    menu_item = load_menu_items()[0]
    response = MenuItemResponse.model_validate(menu_item)

    assert response.id == 12
    assert response.restaurant_id == 5
    assert response.name == "Test Pasta"
    assert response.base_price == 14.5
    assert response.estimated_price == 14.5


def test_menu_data_persists_by_restaurant_and_next_id_advances(monkeypatch, tmp_path):
    menu_items_csv_path = tmp_path / "menu_items.csv"
    monkeypatch.setenv("MENU_ITEMS_CSV_PATH", str(menu_items_csv_path))

    append_menu_item(
        MenuItemRecord(
            id=21,
            restaurant_id=3,
            name="Campus Burger",
            base_price=11.25,
            estimated_price=11.25,
        )
    )

    assert load_menu_items_for_restaurant(3) == [
        MenuItemRecord(
            id=21,
            restaurant_id=3,
            name="Campus Burger",
            base_price=11.25,
            estimated_price=11.25,
            description=None,
            category=None,
        )
    ]
    assert next_menu_item_id() == 22


def test_append_menu_item_rejects_negative_base_price(monkeypatch, tmp_path):
    menu_items_csv_path = tmp_path / "menu_items.csv"
    monkeypatch.setenv("MENU_ITEMS_CSV_PATH", str(menu_items_csv_path))

    with pytest.raises(ValueError, match="base_price"):
        append_menu_item(
            MenuItemRecord(
                id=30,
                restaurant_id=4,
                name="Invalid Soup",
                base_price=-1.0,
                estimated_price=9.5,
            )
        )

    assert load_menu_items() == []


def test_append_menu_item_rejects_negative_estimated_price(monkeypatch, tmp_path):
    menu_items_csv_path = tmp_path / "menu_items.csv"
    monkeypatch.setenv("MENU_ITEMS_CSV_PATH", str(menu_items_csv_path))

    with pytest.raises(ValueError, match="estimated_price"):
        append_menu_item(
            MenuItemRecord(
                id=31,
                restaurant_id=4,
                name="Invalid Salad",
                base_price=9.5,
                estimated_price=-1.0,
            )
        )

    assert load_menu_items() == []


def test_append_menu_item_rejects_empty_name(monkeypatch, tmp_path):
    menu_items_csv_path = tmp_path / "menu_items.csv"
    monkeypatch.setenv("MENU_ITEMS_CSV_PATH", str(menu_items_csv_path))

    with pytest.raises(ValueError, match="name"):
        append_menu_item(
            MenuItemRecord(
                id=32,
                restaurant_id=4,
                name="   ",
                base_price=9.5,
                estimated_price=9.5,
            )
        )

    assert load_menu_items() == []
