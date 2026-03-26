import os

from backend.app.menu_storage import MenuItemRecord, append_menu_item, load_menu_items
from backend.app.restaurant_storage import RestaurantRecord, append_restaurant, load_restaurants
from backend.services.virtual_menu import virtual_menu_for_restaurant

CUISINES = ["American", "Asian", "Italian", "Mediterranean", "Mexican"]


def check_restaurants_exist() -> None:
    if os.environ.get("SKIP_RESTAURANT_BOOTSTRAP"):
        return
    if load_restaurants():
        return

    for rid in range(1, 101):
        append_restaurant(
            RestaurantRecord(
                id=rid,
                name=f"Restaurant {rid}",
                cuisine_type=CUISINES[(rid - 1) % len(CUISINES)],
                address=f"City {(rid % 10) + 1}, Street {rid}",
            )
        )


def check_menu_items_exist() -> None:
    if os.environ.get("SKIP_RESTAURANT_BOOTSTRAP"):
        return
    if load_menu_items():
        return

    for restaurant in load_restaurants():
        for menu_item in virtual_menu_for_restaurant(restaurant.id):
            append_menu_item(
                MenuItemRecord(
                    id=menu_item.id,
                    restaurant_id=menu_item.restaurant_id,
                    name=menu_item.name,
                    base_price=menu_item.base_price,
                    estimated_price=menu_item.base_price,
                    description=menu_item.description,
                )
            )
