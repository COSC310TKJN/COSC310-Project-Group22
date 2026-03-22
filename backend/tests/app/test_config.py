from backend.app.config import Settings


def test_get_settings_uses_environment_value(monkeypatch):
    monkeypatch.setenv("APP_NAME", "Test App")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")

    settings = Settings()

    assert settings.APP_NAME == "Test App"
    assert settings.DATABASE_URL == "sqlite:///./test.db"


def test_get_settings_uses_default_value(monkeypatch):
    monkeypatch.delenv("APP_NAME", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    settings = Settings()

    assert settings.APP_NAME == "Food Delivery Backend"
    assert settings.DATABASE_URL == "sqlite:///./food_delivery.db"
