from typing import Literal
from pydantic import BaseModel, Field


class UserRegisterRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[A-Za-z0-9_]+$",
        description="Unique username using letters, numbers, or underscores.",
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Plain password that will be hashed before storing.",
    )
    role: Literal["user", "manager"] = Field(
        default="user",
        description="Account role that controls protected endpoint access.",
    )


class UserRegisterResponse(BaseModel):
    id: int
    username: str
    is_manager: bool
    role: Literal["user", "manager"]
    message: str = "User registered successfully."


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserLoginResponse(BaseModel):
    id: int
    username: str
    is_manager: bool
    role: Literal["user", "manager"]
    message: str = "Login successful."
