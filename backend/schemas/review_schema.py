from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReviewRequest(BaseModel):
    order_id: int = Field(..., description="Order in Review")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    review_text: Optional[str] = Field(None, max_length=2000)


class ReviewResponse(BaseModel):
    id: int
    order_id: int
    user_id: str
    restaurant_id: int
    rating: int
    review_text: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RestaurantRatingResponse(BaseModel):
    restaurant_id: int
    average_rating: float
    review_count: int

    model_config = {"from_attributes": True}
  
