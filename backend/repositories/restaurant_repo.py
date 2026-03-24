from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.models.restaurant import Restaurant


def get_all_restaurants(
    db: Session,
    cuisine=None,
    skip=0,
    limit=20,
):
    query = db.query(Restaurant)
    if cuisine:
        query = query.filter(Restaurant.cuisine_type == cuisine)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total


def get_restaurant_by_id(db: Session, restaurant_id):
    return db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()


def get_restaurant_ids(db: Session, restaurant_id=None):
    if restaurant_id is not None:
        row = db.query(Restaurant.id).filter(Restaurant.id == restaurant_id).first()
        return [row[0]] if row else []
    return [r[0] for r in db.query(Restaurant.id).all()]


def search_restaurants(
    db: Session,
    q,
    cuisine=None,
    skip=0,
    limit=20,
):
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
