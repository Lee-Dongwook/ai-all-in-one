from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    COOKIE_SECURE: Literal["auto", "true", "false"] = "auto"
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_DEFAULT_MODEL: str = "llama3.2:3b"
    OLLAMA_TIMEOUT_SECONDS: float = Field(default=60, gt=0, le=600)

    @field_validator("COOKIE_SECURE", mode="before")
    @classmethod
    def _cookie_secure_blank_is_auto(cls, value: object) -> object:
        return (value.strip().lower() or "auto") if isinstance(value, str) else value

    @field_validator("OLLAMA_BASE_URL", mode="before")
    @classmethod
    def _normalize_ollama_base_url(cls, value: object) -> object:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("OLLAMA_BASE_URL must be a non-empty URL")
        return value.strip().rstrip("/")


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
