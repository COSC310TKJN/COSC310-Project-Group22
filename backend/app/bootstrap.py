import os

from backend.app.restaurant_storage import RestaurantRecord, append_restaurant, load_restaurants

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
