"""Configuration for Krama Core clients."""

from __future__ import annotations

from urllib.parse import urlparse

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class KramaConfig(BaseSettings):
    """Runtime configuration loaded from arguments or `KRAMA_` env vars."""

    client_id: str = Field(min_length=1)
    client_secret: SecretStr = Field(min_length=1)
    base_url: str = "https://dev.abdm.gov.in"
    callback_url: str = ""
    timeout: float = Field(default=30.0, gt=0, le=120)
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_base_delay: float = Field(default=0.25, ge=0, le=10)

    model_config = SettingsConfigDict(
        env_prefix="KRAMA_",
        extra="ignore",
        str_strip_whitespace=True,
    )

    @field_validator("base_url", "callback_url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        if not value:
            return value

        parsed = urlparse(value)
        if parsed.scheme not in {"https", "http"} or not parsed.netloc:
            raise ValueError("URL must include http(s) scheme and host")

        is_local = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
        if parsed.scheme != "https" and not is_local:
            raise ValueError("URL must use https unless it targets localhost")

        return value.rstrip("/")
