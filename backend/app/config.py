from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Food Delivery Backend"
    FIXED_DELIVERY_DISTANCE_KM: float = 5.0

    model_config = {"env_file": ".env"}


settings = Settings()
