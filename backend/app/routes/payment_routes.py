from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.schemas.payment_schema import PaymentRequest, PaymentResponse, PaymentStatusResponse
from backend.services import payment_service

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/", response_model=PaymentResponse, status_code=201)
def submit_payment(request: PaymentRequest, db: Session = Depends(get_db)):
    payment = payment_service.process_payment(db, request)
    return payment


@router.get("/{payment_id}", response_model=PaymentStatusResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    return payment_service.get_payment_status(db, payment_id)


@router.get("/order/{order_id}", response_model=PaymentStatusResponse)
def get_order_payment(order_id: int, db: Session = Depends(get_db)):
    return payment_service.get_payment_by_order(db, order_id)
