from backend.app.config import get_settings


def test_get_settings_uses_environment_value(monkeypatch):
    monkeypatch.setenv("APP_NAME", "Test App")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")

    settings = get_settings()

    assert settings.app_name == "Test App"
    assert settings.database_url == "sqlite:///./test.db"


def test_get_settings_uses_default_value(monkeypatch):
    monkeypatch.delenv("APP_NAME", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    settings = get_settings()

    assert settings.app_name == "COSC310 Food Delivery API"
    assert settings.database_url == "sqlite:///./food_delivery.db"
