import csv
import os
from pathlib import Path

from backend.app.database import SessionLocal
from backend.models.restaurant import Restaurant

DATASET_PATH = Path(__file__).resolve().parents[2] / "data" / "food_delivery.csv"


def load_restaurants_from_dataset(dataset_path: Path = DATASET_PATH) -> list[Restaurant]:
    restaurants_by_id: dict[int, Restaurant] = {}

    with dataset_path.open(newline="", encoding="utf-8") as dataset_file:
        reader = csv.DictReader(dataset_file)
        for row in reader:
            restaurant_id = int(row["restaurant_id"])
            if restaurant_id in restaurants_by_id:
                continue

            restaurants_by_id[restaurant_id] = Restaurant(
                id=restaurant_id,
                name=f"Restaurant {restaurant_id}",
                cuisine_type=row["preferred_cuisine"],
                address=row["location"],
            )

    return list(restaurants_by_id.values())


def check_restaurants_exist(dataset_path: Path = DATASET_PATH) -> None:
    if os.environ.get("SKIP_RESTAURANT_BOOTSTRAP"):
        return

    db = SessionLocal()
    try:
        if db.query(Restaurant).count() > 0:
            return

        db.add_all(load_restaurants_from_dataset(dataset_path))
        db.commit()
    finally:
        db.close()
