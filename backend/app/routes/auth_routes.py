from fastapi import APIRouter, Depends, Header, HTTPException

from backend.app.roles import Role
from backend.app.security import hash_password, verify_password
from backend.app.user_storage import append_user, find_user_by_id, find_user_by_username, next_user_id
from backend.models.user import User
from backend.schemas.user_schema import (
    UserLoginRequest,
    UserLoginResponse,
    UserRegisterRequest,
    UserRegisterResponse,
)

router = APIRouter()
logged_in_users: set[int] = set()


def login_session(user_id: int) -> None:
    logged_in_users.add(user_id)


def logout_session(user_id: int) -> None:
    logged_in_users.discard(user_id)


def is_logged_in(user_id: int) -> bool:
    return user_id in logged_in_users


def clear_sessions() -> None:
    logged_in_users.clear()


def get_current_user(
    x_user_id: int | None = Header(default=None, alias="X-User-Id"),
) -> User:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Authentication required.")

    user = find_user_by_id(x_user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid user credentials.")
    if not is_logged_in(user.id):
        raise HTTPException(status_code=401, detail="Login required.")

    return user


def require_manager(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_manager:
        raise HTTPException(status_code=403, detail="Manager role required.")

    return current_user


@router.post("/auth/register", response_model=UserRegisterResponse, status_code=201)
def register_user(
    payload: UserRegisterRequest,
) -> UserRegisterResponse:
    existing_user = find_user_by_username(payload.username)
    if existing_user is not None:
        raise HTTPException(status_code=409, detail="Username already exists.")

    user = User(
        id=next_user_id(),
        username=payload.username,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        is_manager=payload.role == Role.MANAGER,
    )
    append_user(user)

    return UserRegisterResponse(
        id=user.id,
        username=user.username,
        is_manager=user.is_manager,
        role=user.role,
    )


@router.post("/auth/login", response_model=UserLoginResponse)
def login_user(
    payload: UserLoginRequest,
) -> UserLoginResponse:
    user = find_user_by_username(payload.username)
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    login_session(user.id)

    return UserLoginResponse(
        id=user.id,
        username=user.username,
        is_manager=user.is_manager,
        role=user.role,
    )


@router.post("/auth/logout")
def logout_user(current_user: User = Depends(get_current_user)) -> dict[str, str]:
    logout_session(current_user.id)
    return {"message": "Logout successful."}


@router.get("/portal/user")
def user_portal(current_user: User = Depends(get_current_user)) -> dict[str, str]:
    return {"message": f"Welcome {current_user.username}. User portal access granted."}


@router.get("/portal/manager")
def manager_portal(current_user: User = Depends(require_manager)) -> dict[str, str]:
    return {"message": f"Welcome {current_user.username}. Manager portal access granted."}
