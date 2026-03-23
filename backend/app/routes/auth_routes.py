from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.security import hash_password
from backend.models.user import User
from backend.schemas.user_schema import UserRegisterRequest, UserRegisterResponse

router = APIRouter()



@router.post("/auth/register", response_model=UserRegisterResponse, status_code=201)
def register_user(
    payload: UserRegisterRequest,
    db: Session = Depends(get_db),
) -> UserRegisterResponse:
    existing_user = db.query(User).filter(User.username == payload.username).first()
    if existing_user is not None:
        raise HTTPException(status_code=409, detail="Username already exists.")

    user = User(
        username=payload.username,
        hashed_password=hash_password(payload.password),        
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserRegisterResponse(
        id=user.id,
        username=user.username       
    )
