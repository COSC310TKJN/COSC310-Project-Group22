from math import ceil

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.repositories import restaurant_repo
from backend.schemas.restaurant_schema import (
    MenuItemListResponse,
    PaginatedMenuItemResponse,
    PaginatedRestaurantResponse,
    RestaurantDetailResponse,
    RestaurantResponse,
)
from backend.services import description_service
from backend.services import pricing_service
from backend.services import virtual_menu


def _to_menu_item_response(item, estimated_price, description):
    return MenuItemListResponse(
        id=item.id,
        name=item.name,
        estimated_price=estimated_price,
        description=description or description_service.get_item_description(
            item.name, item.restaurant_id
        ),
    )


def browse_restaurants(
    db: Session,
    cuisine=None,
    page=1,
    page_size=20,
):
    skip = (page - 1) * page_size
    items, total = restaurant_repo.get_all_restaurants(
        db, cuisine=cuisine, skip=skip, limit=page_size
    )
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    return PaginatedRestaurantResponse(
        items=[RestaurantResponse.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def get_restaurant_detail(db: Session, restaurant_id):
    restaurant = restaurant_repo.get_restaurant_by_id(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    menu_items = virtual_menu.virtual_menu_for_restaurant(restaurant_id)
    menu_responses = []
    for item in menu_items:
        estimated = pricing_service.calculate_estimated_price(item.base_price)
        desc = item.description or description_service.get_item_description(
            item.name, item.restaurant_id
        )
        menu_responses.append(_to_menu_item_response(item, estimated, desc))

    return RestaurantDetailResponse(
        id=restaurant.id,
        name=restaurant.name,
        cuisine_type=restaurant.cuisine_type,
        address=restaurant.address,
        menu_items=menu_responses,
    )

def get_restaurant_menu(
    db: Session,
    restaurant_id,
):
    restaurant = restaurant_repo.get_restaurant_by_id(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    items = virtual_menu.virtual_menu_for_restaurant(restaurant_id)
    return [
        _to_menu_item_response(
            item,
            pricing_service.calculate_estimated_price(item.base_price),
            item.description
            or description_service.get_item_description(item.name, item.restaurant_id),
        )
        for item in items
    ]


def search_restaurants(
    db: Session,
    q,
    cuisine=None,
    page=1,
    page_size=20,
):
    skip = (page - 1) * page_size
    items, total = restaurant_repo.search_restaurants(
        db, q=q, cuisine=cuisine, skip=skip, limit=page_size
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
    db: Session,
    q,
    restaurant_id=None,
    page=1,
    page_size=20,
):
    q_lower = q.lower()
    matches = []
    for rid in restaurant_repo.get_restaurant_ids(db, restaurant_id):
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
            pricing_service.calculate_estimated_price(item.base_price),
            item.description
            or description_service.get_item_description(item.name, item.restaurant_id),
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
