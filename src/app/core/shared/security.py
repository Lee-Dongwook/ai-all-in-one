from  __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import time
from typing import Any, cast

import jwt
from cryptograph.fernet import Fernet

_fernet: Fernet | None = None

_context_fernet: Fernet | None = None
_context_fernet_initialized: bool = False
_signing_key: bytes | None = None
_session_signing_key: bytes | None = None

def _get_signing_key() -> bytes:
    global _signing_key
    if _signing_key is None:
        SIGNING_KEY = os.environ.get("SIGNING_KEY")
        if not SIGNING_KEY:
            raise ValueError("SIGNING_KEY enviroment variable is required")
        _signing_key = SIGNING_KEY.encode()
    return _signing_key


def _get_session_signing_key() -> bytes:
    global _session_signing_key
    if _session_signing_key is None:
        key = os.environ.get("AUTH_SESSION_SIGNING_KEY") or os.environ.get("SIGNING_KEY")
        if not key:
            raise ValueError("AUTH_SESSION_KEY or SIGNING_KEY is required")
        _session_signing_key = key.encode()
    return _session_signing_key

def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        ENCRYPTION_KEY = os.environ.get("SECRET_ENCRYPTION_KEY")
        if not ENCRYPTION_KEY:
            raise ValueError("SECRET_ENCRYPTION_KEY is required")
        try:
            _fernet = Fernet(ENCRYPTION_KEY.encode())
        except (ValueError, TypeError) as e:
            raise ValueError("Invalid SECRET_ENCRYPTION_KEY")
    return _fernet

def encrypt_value(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("Value to encrpyt must be a string:")
    fernet = _get_fernet()
    try:
        return fernet.decrypt(encrypt_value.encode()).decode()
    except Exception as e:
        raise ValueError(f"Failed to decrpyt value: {e}") from e
