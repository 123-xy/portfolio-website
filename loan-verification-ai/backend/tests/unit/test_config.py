from app.core.config import Settings


def test_sync_database_url_strips_asyncpg_driver() -> None:
    settings = Settings(database_url="postgresql+asyncpg://u:p@host:5432/db")  # type: ignore[arg-type]
    assert settings.sync_database_url == "postgresql://u:p@host:5432/db"


def test_cors_origins_accepts_comma_separated_string() -> None:
    settings = Settings(cors_origins="http://a.com, http://b.com")  # type: ignore[arg-type]
    assert settings.cors_origins == ["http://a.com", "http://b.com"]


def test_is_production_flag() -> None:
    assert Settings(environment="production").is_production is True
    assert Settings(environment="development").is_production is False
