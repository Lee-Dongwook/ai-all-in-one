import os

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
import yaml
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, Response
from scalar_fastapi import get_scalar_api_reference

app = FastAPI(
    title="AI-All-In-One API",
    description="AI All In One Project API",
    version = "0.1.0"
)

@app.get("/openapi.yaml", include_in_schema=False)
def get_openapi_yaml() -> Response:
    openapi_schema = app.openapi()
    openapi_yaml = yaml.dump(openapi_schema, sort_keys=False, allow_unicode=True)
    return Response(content=openapi_yaml, media_type="text/yaml")

if __name__ == "__main__":
    uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            proxy_headers=True,
        )
