from typing import Optional

from pydantic import BaseModel


class MenuItemResponse(BaseModel):
    id: int
    restaurant_id: int
    name: str
    base_price: float
    estimated_price: float
    description: Optional[str] = None
    category: Optional[str] = None

    model_config = {"from_attributes": True}


class MenuItemListResponse(BaseModel):
    id: int
    name: str
    estimated_price: float
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class RestaurantResponse(BaseModel):
    id: int
    name: str
    cuisine_type: str
    address: Optional[str] = None
    rating: float = 0.0

    model_config = {"from_attributes": True}


class RestaurantDetailResponse(RestaurantResponse):
    menu_items: list[MenuItemListResponse] = []


class PaginatedRestaurantResponse(BaseModel):
    items: list[RestaurantResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedMenuItemResponse(BaseModel):
    items: list[MenuItemListResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
