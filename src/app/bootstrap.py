"""HTTP application entry point.

Keep framework wiring here so the root ``main.py`` and LangGraph can import the
same application without duplicating configuration.
"""

from __future__ import annotations

import yaml
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response

from .api.ollama import router as ollama_router
from .core.shared.errors import AppError


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI-All-In-One API",
        description="AI All In One Project API",
        version="0.1.0",
    )

    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status.value,
            content=exc.body(),
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"error": "validation_error", "details": exc.errors()},
        )

    @app.get("/health", tags=["system"])
    async def health_check() -> dict[str, str]:
        """Lightweight endpoint for local checks and deployment probes."""
        return {"status": "ok"}

    app.include_router(ollama_router)

    @app.get("/openapi.yaml", include_in_schema=False)
    async def get_openapi_yaml() -> Response:
        openapi_yaml = yaml.safe_dump(
            app.openapi(), sort_keys=False, allow_unicode=True
        )
        return Response(content=openapi_yaml, media_type="application/yaml")

    return app


app = create_app()
