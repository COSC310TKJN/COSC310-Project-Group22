import os
from backend.app.database import SessionLocal
from backend.models.restaurant import Restaurant

CUISINES = ["American", "Asian", "Italian", "Mediterranean", "Mexican"]

def check_restaurants_exist() -> None:
    if os.environ.get("SKIP_RESTAURANT_BOOTSTRAP"):
        return
    db = SessionLocal()
    try:
        if db.query(Restaurant).count() > 0:
            return
        for rid in range(1, 101):
            db.add(
                Restaurant(
                    id=rid,
                    name=f"Restaurant {rid}",
                    cuisine_type=CUISINES[(rid - 1) % len(CUISINES)],
                    address=f"City {(rid % 10) + 1}, Street {rid}",
                    rating=round(3.5 + (rid % 15) / 10, 1),
                )
            )
        db.commit()
    finally:
        db.close()
