from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.menu_storage import (
    MenuItemRecord,
    append_menu_item,
    next_menu_item_id,
)
from backend.app.restaurant_storage import (
    RestaurantRecord,
    append_restaurant,
    find_restaurant_by_id,
    next_restaurant_id,
)
from backend.app.routes.auth_routes import require_manager
from backend.schemas.restaurant_schema import (
    MenuItemCreateRequest,
    MenuItemListResponse,
    MenuItemResponse,
    PaginatedRestaurantResponse,
    RestaurantCreateRequest,
    RestaurantDetailResponse,
    RestaurantResponse,
)
from backend.services import restaurant_service

router = APIRouter(tags=["Restaurants"])


@router.get("/restaurants/search", response_model=PaginatedRestaurantResponse)
def search_restaurants(
    q: str = Query(...),
    page: int = 1,
    page_size: int = 20,
    cuisine: str | None = None,
):
    return restaurant_service.search_restaurants(
        q=q, cuisine=cuisine, page=page, page_size=page_size
    )


@router.get("/restaurants", response_model=PaginatedRestaurantResponse)
def list_restaurants(
    page: int = 1,
    page_size: int = 20,
    cuisine: str | None = None,
):
    return restaurant_service.browse_restaurants(
        cuisine=cuisine, page=page, page_size=page_size
    )


@router.post("/restaurants", response_model=RestaurantResponse, status_code=201)
def create_restaurant(
    payload: RestaurantCreateRequest,
    current_user=Depends(require_manager),
):
    restaurant = RestaurantRecord(
        id=next_restaurant_id(),
        name=payload.name,
        cuisine_type=payload.cuisine_type,
        address=payload.address,
    )
    append_restaurant(restaurant)
    return RestaurantResponse.model_validate(restaurant)


@router.get("/restaurants/{restaurant_id}", response_model=RestaurantDetailResponse)
def get_restaurant(restaurant_id: int):
    return restaurant_service.get_restaurant_detail(restaurant_id)


@router.get(
    "/restaurants/{restaurant_id}/menu",
    response_model=list[MenuItemListResponse],
)
def get_restaurant_menu(restaurant_id: int):
    return restaurant_service.get_restaurant_menu(restaurant_id)


@router.post("/menu-items", response_model=MenuItemResponse, status_code=201)
def create_menu_item(
    payload: MenuItemCreateRequest,
    current_user=Depends(require_manager),
):
    if find_restaurant_by_id(payload.restaurant_id) is None:
        raise HTTPException(status_code=400, detail="Valid restaurant_id is required.")

    menu_item = MenuItemRecord(
        id=next_menu_item_id(),
        restaurant_id=payload.restaurant_id,
        name=payload.name,
        base_price=payload.base_price,
        estimated_price=payload.estimated_price,
        description=payload.description,
        category=payload.category,
    )
    append_menu_item(menu_item)
    return MenuItemResponse.model_validate(menu_item)
