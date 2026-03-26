from dataclasses import dataclass

from backend.app.roles import Role


@dataclass(slots=True)
class User:
    id: int
    username: str
    hashed_password: str
    role: str = Role.USER
    is_manager: bool = False
