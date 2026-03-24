from dataclasses import dataclass

FOOD_ITEMS = [
    "Taccos", "Briyani rice", "Pasta", "Sushi", "Whole cake", "Salad",
    "Burritos", "Chicken wings", "Soup", "Cookie", "CoffeeBoba tea",
    "Chicken pie", "Chicken rice", "Beef pie", "Dumplings", "Shawarma",
    "Pizza", "Cup cake", "PastrySmoothie", "Burger", "Fried chicken",
]


@dataclass(frozen=True)
class VirtualMenuItem:
    id: int
    restaurant_id: int
    name: str
    base_price: float
    description: str | None =None


def virtual_menu_for_restaurant(restaurant_id: int) -> list[VirtualMenuItem]:
    if restaurant_id < 1:
        return []
    start = (restaurant_id - 1) * 3 % len(FOOD_ITEMS)
    names = (FOOD_ITEMS[start:] + FOOD_ITEMS[:start])[:8]
    items = []
    for idx, name in enumerate(names):
        base = round(10.0 + (restaurant_id * 13 + idx * 7 + len(name)) % 100 / 10, 2)
        items.append(
            VirtualMenuItem(
                id=restaurant_id * 1000 + idx + 1,
                restaurant_id=restaurant_id,
                name=name,
                base_price=base,
            )
        )
    return items
