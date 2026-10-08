from __future__ import annotations

from enum import Enum
from http import HTTPStatus
from typing import Any, ClassVar

class ErrorCode(str, Enum):
    ETAG_CONFLICT = "etag_conflict"
    OLLAMA_UNAVAILABLE = "ollama_unavailable"
    OLLAMA_INVALID_RESPONSE = "ollama_invalid_response"

class AppError(Exception):
    status: ClassVar[HTTPStatus] = HTTPStatus.BAD_REQUEST
    headers: dict[str, str] | None = None

    def __init__(self, code: ErrorCode, message: str | None, **fields: Any) -> None:
        super().__init__(message if message is not None else code.value)
        self.code = code
        self.message = message
        self.fields = fields
    
    def body(self) -> dict[str, Any]:
        data: dict[str, Any] = {"error": self.code.value}
        if self.message is not None:
            data["message"] = self.message
        return {**data, **self.fields}

class BadRequest(AppError):
    status = HTTPStatus.BAD_REQUEST


class Forbidden(AppError):
    status = HTTPStatus.FORBIDDEN


class NotFound(AppError):
    status = HTTPStatus.NOT_FOUND


class Conflict(AppError):
    status = HTTPStatus.CONFLICT


class Gone(AppError):
    status = HTTPStatus.GONE


class Unprocessable(AppError):
    status = HTTPStatus.UNPROCESSABLE_ENTITY


class ServiceUnavailable(AppError):
    status = HTTPStatus.SERVICE_UNAVAILABLE
