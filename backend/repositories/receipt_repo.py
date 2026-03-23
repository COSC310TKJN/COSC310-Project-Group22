from sqlalchemy.orm import Session

from backend.models.receipt import Receipt


def create_receipt(db: Session, receipt: Receipt) -> Receipt:
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    return receipt


def get_receipt_by_payment_id(db: Session, payment_id: int) -> Receipt | None:
    return db.query(Receipt).filter(Receipt.payment_id == payment_id).first()


def get_receipt_by_order_id(db: Session, order_id: int) -> Receipt | None:
    return db.query(Receipt).filter(Receipt.order_id == order_id).first()
