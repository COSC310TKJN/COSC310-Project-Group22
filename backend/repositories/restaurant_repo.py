from backend.app.restaurant_storage import (
    RestaurantRecord,
    find_restaurant_by_id,
    load_restaurants,
)


def _filter_by_cuisine(restaurants, cuisine):
    if not cuisine:
        return restaurants
    return [r for r in restaurants if r.cuisine_type == cuisine]


def get_all_restaurants(
    cuisine=None,
    skip=0,
    limit=20,
):
    rows = _filter_by_cuisine(load_restaurants(), cuisine)
    total = len(rows)
    return rows[skip : skip + limit], total


def get_restaurant_by_id(restaurant_id):
    return find_restaurant_by_id(restaurant_id)


def get_restaurant_ids(restaurant_id=None):
    if restaurant_id is not None:
        return [restaurant_id] if get_restaurant_by_id(restaurant_id) else []
    return [r.id for r in load_restaurants()]


def search_restaurants(
    q,
    cuisine=None,
    skip=0,
    limit=20,
):
    q_lower = q.lower()
    rows = [
        r
        for r in load_restaurants()
        if q_lower in r.name.lower() or q_lower in r.cuisine_type.lower()
    ]
    rows = _filter_by_cuisine(rows, cuisine)
    total = len(rows)
    return rows[skip : skip + limit], total
