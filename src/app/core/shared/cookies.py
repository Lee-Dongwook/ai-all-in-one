from __future__ import annotations

from typing import Literal

from starlette.requests import HTTPConnection
from starlette.responses import Response

SameSite = Literal["lax", "strict", "none"]

from .config import get_settings

def cookie_is_secure(conn: HTTPConnection, samesite: SameSite):
    if samesite == "none":
        return True
    mode = get_settings().COOKIE_SECURE
    if mode != "auto":
        return mode == "true"
    return conn.url.scheme == "https"


def set_cookie(
    response: Response,
    conn: HTTPConnection,
    key: str,
    value: str,
    *,
    max_age: int,
    samesite: SameSite,
    httponly: bool = True,
) -> None:
    response.set_cookie(
        key=key,
        value=value,
        max_age=max_age,
        httponly=httponly,
        samesite=samesite,
        secure=cookie_is_secure(conn, samesite)
    )
