from math import ceil

from fastapi import HTTPException

from backend.repositories import restaurant_repo
from backend.schemas.restaurant_schema import (
    MenuItemListResponse,
    PaginatedMenuItemResponse,
    PaginatedRestaurantResponse,
    RestaurantDetailResponse,
    RestaurantResponse,
)
from backend.app.menu_storage import load_menu_items_for_restaurant, MenuItemRecord
from backend.services.pricing_service import PricingService
from backend.services import virtual_menu
from backend.services import description_service



def _to_menu_item_response(item, estimated_price: float):
    return MenuItemListResponse(
        id=item.id,
        name=item.name,
        estimated_price=estimated_price,
        description=item.description
        or description_service.get_item_description(item.name, item.restaurant_id),
    )


def browse_restaurants(
    cuisine: str | None = None,
    page: int = 1,
    page_size: int = 20,
):
    skip = (page - 1) * page_size
    items, total = restaurant_repo.get_all_restaurants(
        cuisine=cuisine, skip=skip, limit=page_size
    )
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    return PaginatedRestaurantResponse(
        items=[RestaurantResponse.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def _all_menu_items(restaurant_id: int):
    virtual_items = virtual_menu.virtual_menu_for_restaurant(restaurant_id)
    csv_items = load_menu_items_for_restaurant(restaurant_id)
    combined = []
    for item in virtual_items:
        estimated = PricingService.calculate_estimated_price(item.base_price)
        combined.append(_to_menu_item_response(item, estimated))
    for item in csv_items:
        combined.append(_to_menu_item_response(item, item.estimated_price))
    return combined


def get_restaurant_detail(restaurant_id: int):
    restaurant = restaurant_repo.get_restaurant_by_id(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return RestaurantDetailResponse(
        id=restaurant.id,
        name=restaurant.name,
        cuisine_type=restaurant.cuisine_type,
        address=restaurant.address,
        menu_items=_all_menu_items(restaurant_id),
    )

def get_restaurant_menu(
    restaurant_id: int,
):
    restaurant = restaurant_repo.get_restaurant_by_id(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return _all_menu_items(restaurant_id)


def search_restaurants(
    q: str,
    cuisine: str | None = None,
    page: int = 1,
    page_size: int = 20,
):
    skip = (page - 1) * page_size
    items, total = restaurant_repo.search_restaurants(
        q=q, cuisine=cuisine, skip=skip, limit=page_size
    )
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    return PaginatedRestaurantResponse(
        items=[RestaurantResponse.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )

def search_items(
    q: str,
    restaurant_id: int | None = None,
    page: int = 1,
    page_size: int = 20,
):
    q_lower = q.lower()
    matches = []
    for rid in restaurant_repo.get_restaurant_ids(restaurant_id):
        for item in virtual_menu.virtual_menu_for_restaurant(rid):
            if q_lower in item.name.lower():
                matches.append(item)

    total = len(matches)
    skip = (page - 1) * page_size
    page_items = matches[skip : skip + page_size]
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    result_items = [
        _to_menu_item_response(
            item,
            PricingService.calculate_estimated_price(item.base_price),
        )
        for item in page_items
    ]
    return PaginatedMenuItemResponse(
        items=result_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
