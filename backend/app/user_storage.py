import os
from pathlib import Path

from backend.app import csv_storage
from backend.models.user import User

USER_HEADERS = ["id", "username", "hashed_password", "role", "is_manager"]


def get_users_csv_path() -> Path:
    return Path(os.environ.get("AUTH_USERS_CSV_PATH", "data/users.csv"))


def ensure_users_csv_exists() -> Path:
    path = get_users_csv_path()
    return csv_storage.ensure_csv_file(path, USER_HEADERS)


def row_to_user(row: dict[str, str]) -> User:
    return User(
        id=int(row["id"]),
        username=row["username"],
        hashed_password=row["hashed_password"],
        role=row["role"],
        is_manager=row["is_manager"] == "True",
    )


def user_to_row(user: User) -> dict[str, str]:
    return {
        "id": str(user.id),
        "username": user.username,
        "hashed_password": user.hashed_password,
        "role": user.role,
        "is_manager": str(user.is_manager),
    }


def load_users() -> list[User]:
    path = ensure_users_csv_exists()
    return [row_to_user(row) for row in csv_storage.read_rows(path, USER_HEADERS)]


def find_user_by_id(user_id: int) -> User | None:
    for user in load_users():
        if user.id == user_id:
            return user
    return None


def find_user_by_username(username: str) -> User | None:
    for user in load_users():
        if user.username == username:
            return user
    return None


def next_user_id() -> int:
    rows = csv_storage.read_rows(ensure_users_csv_exists(), USER_HEADERS)
    return csv_storage.next_int_id(rows)


def append_user(user: User) -> None:
    path = ensure_users_csv_exists()
    csv_storage.append_row(path, USER_HEADERS, user_to_row(user))
