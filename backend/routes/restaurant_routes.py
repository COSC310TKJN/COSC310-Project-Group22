from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.schemas.restaurant_schema import (
    MenuItemListResponse,
    PaginatedMenuItemResponse,
    PaginatedRestaurantResponse,
    RestaurantDetailResponse,
)
from backend.services import restaurant_service

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.get("/", response_model=PaginatedRestaurantResponse)
def browse_restaurants(
    cuisine: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return restaurant_service.browse_restaurants(
        db, cuisine=cuisine, page=page, page_size=page_size
    )


@router.get("/search/restaurants", response_model=PaginatedRestaurantResponse)
def search_restaurants(
    q: str = Query(..., min_length=1),
    cuisine: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return restaurant_service.search_restaurants(
        db, q=q, cuisine=cuisine, page=page, page_size=page_size
    )


@router.get("/search/items", response_model=PaginatedMenuItemResponse)
def search_items(
    q: str = Query(..., min_length=1),
    restaurant_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return restaurant_service.search_items(
        db, q=q, restaurant_id=restaurant_id, page=page, page_size=page_size
    )


@router.get("/{restaurant_id}", response_model=RestaurantDetailResponse)
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    return restaurant_service.get_restaurant_detail(db, restaurant_id)


@router.get("/{restaurant_id}/menu", response_model=list[MenuItemListResponse])
def get_restaurant_menu(restaurant_id: int, db: Session = Depends(get_db)):
    return restaurant_service.get_restaurant_menu(db, restaurant_id)
