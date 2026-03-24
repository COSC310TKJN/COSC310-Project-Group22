from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app import bootstrap
from backend.app.database import Base
from backend.models.restaurant import Restaurant


def test_load_restaurants_from_dataset_builds_unique_restaurant_records(tmp_path: Path):
    dataset_path = tmp_path / "restaurants.csv"
    dataset_path.write_text(
        "\n".join(
            [
                "restaurant_id,preferred_cuisine,location",
                "3,Italian,City_8",
                "3,Italian,City_8",
                "7,Asian,City_2",
            ]
        ),
        encoding="utf-8",
    )

    restaurants = bootstrap.load_restaurants_from_dataset(dataset_path)

    assert [restaurant.id for restaurant in restaurants] == [3, 7]
    assert restaurants[0].name == "Restaurant 3"
    assert restaurants[0].cuisine_type == "Italian"
    assert restaurants[0].address == "City_8"
    assert restaurants[1].name == "Restaurant 7"


def test_check_restaurants_exist_persists_restaurants_from_dataset(monkeypatch, tmp_path: Path):
    dataset_path = tmp_path / "restaurants.csv"
    dataset_path.write_text(
        "\n".join(
            [
                "restaurant_id,preferred_cuisine,location",
                "10,Mexican,City_5",
                "12,American,City_1",
            ]
        ),
        encoding="utf-8",
    )

    database_path = tmp_path / "restaurants.db"
    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)
    monkeypatch.delenv("SKIP_RESTAURANT_BOOTSTRAP", raising=False)
    monkeypatch.setattr(bootstrap, "SessionLocal", testing_session_local)

    try:
        bootstrap.check_restaurants_exist(dataset_path)

        db = testing_session_local()
        try:
            restaurants = db.query(Restaurant).order_by(Restaurant.id).all()
            assert [restaurant.id for restaurant in restaurants] == [10, 12]
            assert restaurants[0].name == "Restaurant 10"
            assert restaurants[0].cuisine_type == "Mexican"
            assert restaurants[0].address == "City_5"
        finally:
            db.close()
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
