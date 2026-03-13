from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.schemas.payment_schema import PaymentRequest, PaymentResponse
from backend.services import payment_service

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/methods")
def get_payment_methods():
    return payment_service.get_available_methods()


@router.post("/", response_model=PaymentResponse, status_code=201)
def submit_payment(request: PaymentRequest, db: Session = Depends(get_db)):
    payment = payment_service.process_payment(db, request)
    return payment
