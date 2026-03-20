
"""Centralized application settings for backend services."""

import os
from dataclasses import dataclass


# This dataclass groups environment-based settings in one place for consistent access.
@dataclass(frozen=True)
class Settings:
    app_name: str
    # DATABASE_URL controls where SQLAlchemy stores application data.
    database_url: str


# This helper reads environment variables and falls back to a local SQLite database.
def get_settings() -> Settings:
    app_name = os.getenv("APP_NAME", "COSC310 Food Delivery API")
    # Use a sensible local default so the app can run without extra setup.
    database_url = os.getenv("DATABASE_URL", "sqlite:///./food_delivery.db")
    return Settings(app_name=app_name, database_url=database_url)


# This module-level instance is imported by other backend modules.
settings = get_settings()
