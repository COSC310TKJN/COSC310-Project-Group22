from fastapi import APIRouter, Depends, HTTPException

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
from backend.models.user import User
from backend.schemas.restaurant_schema import (
    MenuItemCreateRequest,
    MenuItemResponse,
    RestaurantCreateRequest,
    RestaurantResponse,
)

router = APIRouter(tags=["Restaurants"])


@router.post("/restaurants", response_model=RestaurantResponse, status_code=201)
def create_restaurant(
    payload: RestaurantCreateRequest,
    current_user: User = Depends(require_manager),
) -> RestaurantResponse:
    restaurant = RestaurantRecord(
        id=next_restaurant_id(),
        name=payload.name,
        cuisine_type=payload.cuisine_type,
        address=payload.address,
    )
    append_restaurant(restaurant)
    return RestaurantResponse.model_validate(restaurant)


@router.post("/menu-items", response_model=MenuItemResponse, status_code=201)
def create_menu_item(
    payload: MenuItemCreateRequest,
    current_user: User = Depends(require_manager),
) -> MenuItemResponse:
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
