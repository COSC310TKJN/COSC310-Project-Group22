from fastapi import APIRouter

from backend.schemas.review_schema import (
    ReviewCreate,
    ReviewResponse,
    RestaurantRatingResponse,
)
from backend.services import review_service

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/", response_model=ReviewResponse, status_code=201)
def submit_review(request: ReviewCreate):
    return review_service.create_review(request)


@router.get("/restaurant/{restaurant_id}", response_model=list[ReviewResponse])
def get_restaurant_reviews(restaurant_id: int):
    return review_service.get_reviews_for_restaurant(restaurant_id)


@router.get("/restaurant/{restaurant_id}/average", response_model=RestaurantRatingResponse)
def get_restaurant_rating(restaurant_id: int):
    return review_service.get_restaurant_average_rating(restaurant_id)


@router.get("/customer/{customer_id}", response_model=list[ReviewResponse])
def get_customer_reviews(customer_id: str):
    return review_service.get_reviews_by_customer(customer_id)


@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(review_id: int):
    return review_service.get_review(review_id)
