from __future__ import annotations

import os

from cryptography.fernet import Fernet, InvalidToken

_fernet: Fernet | None = None

_signing_key: bytes | None = None
_session_signing_key: bytes | None = None


def _get_signing_key() -> bytes:
    global _signing_key
    if _signing_key is None:
        signing_key = os.environ.get("SIGNING_KEY")
        if not signing_key:
            raise ValueError("SIGNING_KEY environment variable is required")
        _signing_key = signing_key.encode()
    return _signing_key


def _get_session_signing_key() -> bytes:
    global _session_signing_key
    if _session_signing_key is None:
        key = os.environ.get("AUTH_SESSION_SIGNING_KEY") or os.environ.get("SIGNING_KEY")
        if not key:
            raise ValueError("AUTH_SESSION_SIGNING_KEY or SIGNING_KEY is required")
        _session_signing_key = key.encode()
    return _session_signing_key

def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        encryption_key = os.environ.get("SECRET_ENCRYPTION_KEY")
        if not encryption_key:
            raise ValueError("SECRET_ENCRYPTION_KEY is required")
        try:
            _fernet = Fernet(encryption_key.encode())
        except (ValueError, TypeError) as exc:
            raise ValueError("Invalid SECRET_ENCRYPTION_KEY") from exc
    return _fernet


def encrypt_value(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("Value to encrypt must be a string")
    fernet = _get_fernet()
    try:
        return fernet.encrypt(value.encode()).decode()
    except (TypeError, ValueError) as exc:
        raise ValueError("Failed to encrypt value") from exc


def decrypt_value(value: str) -> str:
    """Decrypt a value previously returned by :func:`encrypt_value`."""
    if not isinstance(value, str):
        raise TypeError("Value to decrypt must be a string")
    try:
        return _get_fernet().decrypt(value.encode()).decode()
    except (InvalidToken, TypeError, ValueError) as exc:
        raise ValueError("Failed to decrypt value") from exc
