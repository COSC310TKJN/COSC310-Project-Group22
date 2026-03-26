import os
from dataclasses import dataclass
from pathlib import Path

from backend.app import csv_storage

MENU_ITEM_HEADERS = [
    "id",
    "restaurant_id",
    "name",
    "base_price",
    "estimated_price",
    "description",
    "category",
]


@dataclass(frozen=True)
class MenuItemRecord:
    id: int
    restaurant_id: int
    name: str
    base_price: float
    estimated_price: float
    description: str | None = None
    category: str | None = None


def validate_menu_item(menu_item: MenuItemRecord) -> None:
    if not menu_item.name.strip():
        raise ValueError("Menu item name cannot be empty.")
    if menu_item.base_price < 0:
        raise ValueError("Menu item base_price cannot be negative.")
    if menu_item.estimated_price < 0:
        raise ValueError("Menu item estimated_price cannot be negative.")


def get_menu_items_csv_path() -> Path:
    return Path(os.environ.get("MENU_ITEMS_CSV_PATH", "data/menu_items.csv"))


def ensure_menu_items_csv_exists() -> Path:
    return csv_storage.ensure_csv_file(get_menu_items_csv_path(), MENU_ITEM_HEADERS)


def row_to_menu_item(row: dict[str, str]) -> MenuItemRecord:
    return MenuItemRecord(
        id=int(row["id"]),
        restaurant_id=int(row["restaurant_id"]),
        name=row["name"],
        base_price=float(row["base_price"]),
        estimated_price=float(row["estimated_price"]),
        description=row["description"] or None,
        category=row["category"] or None,
    )


def menu_item_to_row(menu_item: MenuItemRecord) -> dict[str, str]:
    return {
        "id": str(menu_item.id),
        "restaurant_id": str(menu_item.restaurant_id),
        "name": menu_item.name,
        "base_price": f"{menu_item.base_price:.2f}",
        "estimated_price": f"{menu_item.estimated_price:.2f}",
        "description": menu_item.description or "",
        "category": menu_item.category or "",
    }


def load_menu_items() -> list[MenuItemRecord]:
    path = ensure_menu_items_csv_exists()
    return [row_to_menu_item(row) for row in csv_storage.read_rows(path, MENU_ITEM_HEADERS)]


def load_menu_items_for_restaurant(restaurant_id: int) -> list[MenuItemRecord]:
    return [item for item in load_menu_items() if item.restaurant_id == restaurant_id]


def append_menu_item(menu_item: MenuItemRecord) -> None:
    validate_menu_item(menu_item)
    path = ensure_menu_items_csv_exists()
    csv_storage.append_row(path, MENU_ITEM_HEADERS, menu_item_to_row(menu_item))


def next_menu_item_id() -> int:
    rows = csv_storage.read_rows(ensure_menu_items_csv_exists(), MENU_ITEM_HEADERS)
    return csv_storage.next_int_id(rows)
