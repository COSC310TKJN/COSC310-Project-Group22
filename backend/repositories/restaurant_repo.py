from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.models.restaurant import Restaurant

def get_all_restaurants(
    db: Session,
    cuisine: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[Restaurant], int]:
    query = db.query(Restaurant)
    if cuisine:
        query = query.filter(Restaurant.cuisine_type == cuisine)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total

def get_restaurant_by_id(db: Session, restaurant_id: int) -> Restaurant | None:
    return db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()


def get_restaurant_ids(db: Session, restaurant_id: int | None = None) -> list[int]:
    if restaurant_id is not None:
        row = db.query(Restaurant.id).filter(Restaurant.id == restaurant_id).first()
        return [row[0]] if row else []
    return [r[0] for r in db.query(Restaurant.id).all()]


def search_restaurants(
    db: Session,
    q: str,
    cuisine: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[Restaurant], int]:
    query = db.query(Restaurant).filter(
        or_(
            Restaurant.name.ilike(f"%{q}%"),
            Restaurant.cuisine_type.ilike(f"%{q}%"),
        )
    )
    if cuisine:
        query = query.filter(Restaurant.cuisine_type == cuisine)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total
