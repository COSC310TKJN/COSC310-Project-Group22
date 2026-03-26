from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Food Delivery Backend"

    model_config = {"env_file": ".env"}


settings = Settings()
