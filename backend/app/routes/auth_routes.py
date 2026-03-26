import os
from pathlib import Path

from fastapi import APIRouter, Depends, Header, HTTPException

from backend.app import csv_storage
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
USER_HEADERS = ["id", "username", "hashed_password", "role", "is_manager"]


def _get_users_csv_path() -> Path:
    return Path(os.environ.get("AUTH_USERS_CSV_PATH", "data/users.csv"))


def _ensure_users_csv_exists() -> Path:
    path = _get_users_csv_path()
    return csv_storage.ensure_csv_file(path, USER_HEADERS)


def _row_to_user(row: dict[str, str]) -> User:
    return User(
        id=int(row["id"]),
        username=row["username"],
        hashed_password=row["hashed_password"],
        role=row["role"],
        is_manager=row["is_manager"] == "True",
    )


def _user_to_row(user: User) -> dict[str, str]:
    return {
        "id": str(user.id),
        "username": user.username,
        "hashed_password": user.hashed_password,
        "role": user.role,
        "is_manager": str(user.is_manager),
    }


def _load_users() -> list[User]:
    path = _ensure_users_csv_exists()
    return [_row_to_user(row) for row in csv_storage.read_rows(path, USER_HEADERS)]


def _find_user_by_id(user_id: int) -> User | None:
    for user in _load_users():
        if user.id == user_id:
            return user
    return None


def _find_user_by_username(username: str) -> User | None:
    for user in _load_users():
        if user.username == username:
            return user
    return None


def _next_user_id() -> int:
    rows = csv_storage.read_rows(_ensure_users_csv_exists(), USER_HEADERS)
    return csv_storage.next_int_id(rows)


def _append_user(user: User) -> None:
    path = _ensure_users_csv_exists()
    csv_storage.append_row(path, USER_HEADERS, _user_to_row(user))


def get_current_user(
    x_user_id: int | None = Header(default=None, alias="X-User-Id"),
) -> User:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Authentication required.")

    user = _find_user_by_id(x_user_id)
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
) -> UserRegisterResponse:
    existing_user = _find_user_by_username(payload.username)
    if existing_user is not None:
        raise HTTPException(status_code=409, detail="Username already exists.")

    user = User(
        id=_next_user_id(),
        username=payload.username,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        is_manager=payload.role == "manager",
    )
    _append_user(user)

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
    user = _find_user_by_username(payload.username)
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
