from pathlib import Path
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource


_DEFAULT_SECRET = "change-me-to-a-random-secret-key"


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/academic_db"
    # External Luna attendance source. Kept optional so a Luna outage or an
    # unconfigured development environment cannot block core Face ID startup.
    LUNA_DATABASE_URL: str | None = None
    SECRET_KEY: str = _DEFAULT_SECRET
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ESNAAD_BASE_URL: str = "http://localhost:5008/api"
    ESNAAD_API_KEY: str = ""
    # Cookie settings for refresh token
    COOKIE_SECURE: bool = False  # Set True in production (HTTPS)
    COOKIE_SAMESITE: str = "lax"  # "strict" | "lax" | "none"

    # LDAP
    LDAP_MOCK: bool = False
    LDAP_SERVER: str = "ldap://localhost:389"
    LDAP_BASE_DN: str = "dc=example,dc=com"
    LDAP_USER_DN_TEMPLATE: str = "uid={username},ou=users,dc=example,dc=com"
    LDAP_SEARCH_FILTER: str = "(uid={username})"

    # Logging
    LOG_LEVEL: str = "INFO"
    SQL_LOG_LEVEL: str = "WARNING"
    # Rotating file log (daily, 14 days) written regardless of how the server
    # is launched, so no shell redirection (`> server.log 2>&1`) is needed.
    LOG_TO_FILE: bool = True
    LOG_DIR: Path = Path(__file__).parent.parent.parent / "logs"

    # When True, unhandled (500) responses expose the exception type, message and
    # a short traceback to the client so the UI can show why it failed. Keep this
    # ON in dev/staging; set False in production to avoid leaking internals.
    DEBUG: bool = True

    DEVICE_API_PASSWORD: str = ""

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173", "http://localhost:3000"]

    # Allow all origins in development (only use in dev, not production!)
    ALLOW_ALL_ORIGINS: bool = True

    model_config = {"env_file": ".env", "extra": "ignore"}

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        **kwargs: Any,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            *kwargs.values(),
        )

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_be_changed(cls, v: str) -> str:
        if v == _DEFAULT_SECRET:
            raise ValueError(
                "SECRET_KEY must be set to a secure random value in .env — "
                "do not use the default in any environment."
            )
        if len(v) < 32:
            ValueError("SECRET_KEY must be at least 32 characters long.")
        return v


settings = Settings()
