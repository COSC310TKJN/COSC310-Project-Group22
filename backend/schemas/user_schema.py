"""Pydantic schemas for user registration endpoints."""

from typing import Literal

from pydantic import BaseModel, Field


# Request payload for registering a new account.
class UserRegisterRequest(BaseModel):
    # Username is normalized and restricted to common safe characters.
    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[A-Za-z0-9_]+$",
        description="Unique username using letters, numbers, or underscores.",
    )

    # Password minimum length helps reject weak credentials at registration time.
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Plain password that will be hashed before storing.",
    )

    # Role selected at account creation to support user vs manager permissions.
    role: Literal["user", "manager"] = Field(
        default="user",
        description="Account role that controls protected endpoint access.",
    )


# Response payload returned after successful user registration.
class UserRegisterResponse(BaseModel):
    # Database id of the newly created user.
    id: int

    # The account username that was created.
    username: str

    # Role flag exposed for client-side role-aware behavior.
    is_manager: bool

    # Canonical role returned to clients for role-based UI and logic.
    role: Literal["user", "manager"]

    # Success message to make API responses explicit.
    message: str = "User registered successfully."
