"""Small async client for the local or private-network Ollama API."""

from __future__ import annotations

from typing import Any

import httpx


class OllamaUnavailableError(Exception):
    """Raised when the configured Ollama server cannot serve a request."""


class OllamaInvalidResponseError(Exception):
    """Raised when Ollama returns a response outside the expected shape."""


class OllamaClient:
    def __init__(
        self,
        base_url: str,
        timeout_seconds: float,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = httpx.Timeout(timeout_seconds)
        self._transport = transport

    async def list_models(self) -> list[dict[str, Any]]:
        payload = await self._request("GET", "/api/tags")
        models = payload.get("models")
        if not isinstance(models, list):
            raise OllamaInvalidResponseError("Ollama returned no model list")
        return [model for model in models if isinstance(model, dict)]

    async def chat(self, *, model: str, message: str) -> str:
        payload = await self._request(
            "POST",
            "/api/chat",
            json={
                "model": model,
                "messages": [{"role": "user", "content": message}],
                "stream": False,
            },
        )
        response_message = payload.get("message")
        if not isinstance(response_message, dict):
            raise OllamaInvalidResponseError("Ollama returned no assistant message")
        content = response_message.get("content")
        if not isinstance(content, str):
            raise OllamaInvalidResponseError("Ollama assistant message has no text")
        return content

    async def _request(
        self, method: str, path: str, **kwargs: Any
    ) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
                transport=self._transport,
            ) as client:
                response = await client.request(method, path, **kwargs)
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise OllamaUnavailableError("Unable to communicate with Ollama") from exc

        if not isinstance(payload, dict):
            raise OllamaInvalidResponseError("Ollama returned an invalid JSON payload")
        return payload
