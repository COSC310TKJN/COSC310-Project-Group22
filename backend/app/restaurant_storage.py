import os
from dataclasses import dataclass
from pathlib import Path

from backend.app import csv_storage

RESTAURANT_HEADERS = ["id", "name", "cuisine_type", "address"]


@dataclass(frozen=True)
class RestaurantRecord:
    id: int
    name: str
    cuisine_type: str
    address: str | None = None


def get_restaurants_csv_path() -> Path:
    return Path(os.environ.get("RESTAURANTS_CSV_PATH", "data/restaurants.csv"))


def ensure_restaurants_csv_exists() -> Path:
    return csv_storage.ensure_csv_file(get_restaurants_csv_path(), RESTAURANT_HEADERS)


def row_to_restaurant(row: dict[str, str]) -> RestaurantRecord:
    return RestaurantRecord(
        id=int(row["id"]),
        name=row["name"],
        cuisine_type=row["cuisine_type"],
        address=row["address"] or None,
    )


def restaurant_to_row(restaurant: RestaurantRecord) -> dict[str, str]:
    return {
        "id": str(restaurant.id),
        "name": restaurant.name,
        "cuisine_type": restaurant.cuisine_type,
        "address": restaurant.address or "",
    }


def load_restaurants() -> list[RestaurantRecord]:
    path = ensure_restaurants_csv_exists()
    return [row_to_restaurant(row) for row in csv_storage.read_rows(path, RESTAURANT_HEADERS)]


def append_restaurant(restaurant: RestaurantRecord) -> None:
    path = ensure_restaurants_csv_exists()
    csv_storage.append_row(path, RESTAURANT_HEADERS, restaurant_to_row(restaurant))


def next_restaurant_id() -> int:
    rows = csv_storage.read_rows(ensure_restaurants_csv_exists(), RESTAURANT_HEADERS)
    return csv_storage.next_int_id(rows)
