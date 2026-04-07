from fastapi import HTTPException

from backend.repositories import review_repo


def create_review(request) -> dict:
    existing = review_repo.get_review_by_order(request.order_id, request.customer_id)
    if existing:
        raise HTTPException(status_code=400, detail="Review already exists for this order")

    data = {
        "customer_id": request.customer_id,
        "order_id": request.order_id,
        "restaurant_id": request.restaurant_id,
        "rating": request.rating,
        "comment": request.comment,
    }

    return review_repo.create_review(data)


def get_review(review_id: int) -> dict:
    review = review_repo.get_review_by_id(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


def get_reviews_for_restaurant(restaurant_id: int) -> list[dict]:
    return review_repo.get_reviews_by_restaurant(restaurant_id)


def get_restaurant_average_rating(restaurant_id: int) -> dict:
    reviews = review_repo.get_reviews_by_restaurant(restaurant_id)
    if not reviews:
        return {
            "restaurant_id": restaurant_id,
            "average_rating": 0.0,
            "total_reviews": 0,
        }
    avg = sum(r["rating"] for r in reviews) / len(reviews)
    return {
        "restaurant_id": restaurant_id,
        "average_rating": round(avg, 2),
        "total_reviews": len(reviews),
    }


def get_reviews_by_customer(customer_id: str) -> list[dict]:
    return review_repo.get_reviews_by_customer(customer_id)
