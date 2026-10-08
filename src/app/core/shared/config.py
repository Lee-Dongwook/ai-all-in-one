from __future__ import annotations

import ipaddress
import logging
import os
from functools import lru_cache
from typing import TYPE_CHECKING, Annotated, Any, Literal, TypeVar

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)

class AppSettings(BaseSettings):
    COOKIE_SECURE: Literal["auto", "true", "false"] = "auto"

    @field_validator("COOKIE_SECURE", mode="before")
    @classmethod
    def _cookie_secure_blank_is_auto(cls, value: object) -> object:
        return (value.strip().lower() or "auto") if isinstance(value, str) else value


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
