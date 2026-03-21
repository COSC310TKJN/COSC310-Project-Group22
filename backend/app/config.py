import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str
    database_url: str


def get_settings() -> Settings:
    app_name = os.getenv("APP_NAME", "COSC310 Food Delivery API")
    database_url = os.getenv("DATABASE_URL", "sqlite:///./food_delivery.db")
    return Settings(app_name=app_name, database_url=database_url)


settings = get_settings()
