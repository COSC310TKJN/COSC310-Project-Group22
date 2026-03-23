from sqlalchemy.orm import Session

from backend.models.payment import Payment


def create_payment(db: Session, payment: Payment) -> Payment:
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def get_payment_by_id(db: Session, payment_id: int) -> Payment | None:
    return db.query(Payment).filter(Payment.id == payment_id).first()


def get_payment_by_order_id(db: Session, order_id: int) -> Payment | None:
    return db.query(Payment).filter(Payment.order_id == order_id).first()


def update_payment_status(db: Session, payment: Payment, status: str) -> Payment:
    payment.status = status
    db.commit()
    db.refresh(payment)
    return payment


def get_payments_by_status(db: Session, status: str):
    return db.query(Payment).filter(Payment.status == status).all()
