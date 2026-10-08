"""HTTP endpoints backed only by a configured on-premises Ollama server."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

from ..core.shared.config import get_settings
from ..core.shared.errors import ErrorCode, ServiceUnavailable
from ..llm.ollama import (
    OllamaClient,
    OllamaInvalidResponseError,
    OllamaUnavailableError,
)

router = APIRouter(tags=["ollama"])


class ModelInfo(BaseModel):
    name: str
    size: int | None = None
    modified_at: str | None = None


class ModelsResponse(BaseModel):
    models: list[ModelInfo]


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    message: str = Field(min_length=1, max_length=32_000)
    model: str | None = Field(default=None, min_length=1, max_length=200)


class ChatResponse(BaseModel):
    model: str
    message: str


def _client() -> OllamaClient:
    settings = get_settings()
    return OllamaClient(
        base_url=settings.OLLAMA_BASE_URL,
        timeout_seconds=settings.OLLAMA_TIMEOUT_SECONDS,
    )


def _service_unavailable(exc: Exception) -> ServiceUnavailable:
    code = (
        ErrorCode.OLLAMA_INVALID_RESPONSE
        if isinstance(exc, OllamaInvalidResponseError)
        else ErrorCode.OLLAMA_UNAVAILABLE
    )
    return ServiceUnavailable(code, "The configured Ollama server is unavailable")


@router.get("/models", response_model=ModelsResponse)
async def list_models() -> ModelsResponse:
    """List models installed on the configured Ollama server."""
    try:
        models = await _client().list_models()
    except (OllamaUnavailableError, OllamaInvalidResponseError) as exc:
        raise _service_unavailable(exc) from exc

    return ModelsResponse(
        models=[
            ModelInfo(
                name=model["name"],
                size=model.get("size"),
                modified_at=model.get("modified_at"),
            )
            for model in models
            if isinstance(model.get("name"), str)
        ]
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Send one user message to an installed Ollama model without streaming."""
    settings = get_settings()
    model = request.model or settings.OLLAMA_DEFAULT_MODEL
    try:
        message = await _client().chat(model=model, message=request.message)
    except (OllamaUnavailableError, OllamaInvalidResponseError) as exc:
        raise _service_unavailable(exc) from exc
    return ChatResponse(model=model, message=message)
