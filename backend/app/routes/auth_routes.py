from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.security import hash_password, verify_password
from backend.models.user import User
from backend.schemas.user_schema import (
    UserLoginRequest,
    UserLoginResponse,
    UserRegisterRequest,
    UserRegisterResponse,
)

router = APIRouter()
logged_in_users: set[int] = set()


def get_current_user(
    x_user_id: int | None = Header(default=None, alias="X-User-Id"),
    db: Session = Depends(get_db),
) -> User:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Authentication required.")

    user = db.query(User).filter(User.id == x_user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid user credentials.")
    if user.id not in logged_in_users:
        raise HTTPException(status_code=401, detail="Login required.")

    return user


def require_manager(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_manager:
        raise HTTPException(status_code=403, detail="Manager role required.")

    return current_user


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
        role=payload.role,
        is_manager=payload.role == "manager",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserRegisterResponse(
        id=user.id,
        username=user.username,
        is_manager=user.is_manager,
        role=user.role,
    )


@router.post("/auth/login", response_model=UserLoginResponse)
def login_user(
    payload: UserLoginRequest,
    db: Session = Depends(get_db),
) -> UserLoginResponse:
    user = db.query(User).filter(User.username == payload.username).first()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    logged_in_users.add(user.id)

    return UserLoginResponse(
        id=user.id,
        username=user.username,
        is_manager=user.is_manager,
        role=user.role,
    )


@router.post("/auth/logout")
def logout_user(current_user: User = Depends(get_current_user)) -> dict[str, str]:
    logged_in_users.discard(current_user.id)
    return {"message": "Logout successful."}


@router.get("/portal/user")
def user_portal(current_user: User = Depends(get_current_user)) -> dict[str, str]:
    return {"message": f"Welcome {current_user.username}. User portal access granted."}


@router.get("/portal/manager")
def manager_portal(current_user: User = Depends(require_manager)) -> dict[str, str]:
    return {"message": f"Welcome {current_user.username}. Manager portal access granted."}
