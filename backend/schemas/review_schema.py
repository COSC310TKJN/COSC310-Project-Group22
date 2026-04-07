from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    customer_id: str
    order_id: int
    restaurant_id: int
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    customer_id: str
    order_id: int
    restaurant_id: int
    rating: int
    comment: Optional[str] = None
    created_at: Optional[datetime] = None


class RestaurantRatingResponse(BaseModel):
    restaurant_id: int
    average_rating: float
    total_reviews: int
