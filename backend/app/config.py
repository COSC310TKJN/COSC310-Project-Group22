from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./food_delivery.db"
    APP_NAME: str = "Food Delivery Backend"

    model_config = {"env_file": ".env"}


settings = Settings()
