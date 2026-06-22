from __future__ import annotations

import json
import os
from contextlib import asynccontextmanager
from typing import Dict, Iterable, List, Optional, Tuple

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response


_HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
    "host",
    "content-length",
}

_DEFAULT_ROUTES: Dict[str, str] = {
    # Default: route car-catalog API to localhost:8001
    "/api/v1/cars": os.getenv("CATALOG_URL", "http://localhost:8001"),
}

_ALLOWED_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
    "HEAD",
]


def _parse_routes() -> List[Tuple[str, str]]:
    raw = os.getenv("GATEWAY_ROUTES")
    if not raw:
        routes = _DEFAULT_ROUTES
    else:
        try:
            routes = json.loads(raw)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid GATEWAY_ROUTES JSON: {e}") from e

        if not isinstance(routes, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in routes.items()):
            raise RuntimeError("GATEWAY_ROUTES must be a JSON object mapping string prefixes to string base URLs")

    normalized: List[Tuple[str, str]] = []
    for prefix, base_url in routes.items():
        if not prefix.startswith("/"):
            prefix = "/" + prefix
        normalized.append((prefix.rstrip("/"), base_url.rstrip("/")))

    # Longest-prefix match
    normalized.sort(key=lambda x: len(x[0]), reverse=True)
    return normalized


def _match_backend(path: str, routes: List[Tuple[str, str]]) -> Optional[str]:
    for prefix, base_url in routes:
        if path == prefix or path.startswith(prefix + "/"):
            return base_url
    return None


def _filtered_headers(headers: Iterable[Tuple[str, str]]) -> Dict[str, str]:
    return {k: v for k, v in headers if k.lower() not in _HOP_BY_HOP_HEADERS}


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.routes = _parse_routes()
    timeout_s = float(os.getenv("GATEWAY_TIMEOUT_SECONDS", "30"))
    chat_timeout_s = float(os.getenv("GATEWAY_CHAT_TIMEOUT_SECONDS", "180"))
    app.state.http = httpx.AsyncClient(timeout=timeout_s, follow_redirects=True)
    app.state.timeout_default = timeout_s
    app.state.timeout_chat = chat_timeout_s
    yield
    await app.state.http.aclose()


app = FastAPI(title="API Gateway", version="0.1.0", lifespan=lifespan)

_cors = os.getenv("GATEWAY_CORS_ORIGINS", "").strip()
if _cors:
    origins = [o.strip() for o in _cors.split(",") if o.strip()]
    if origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def index():
    return {
        "service": "gateway",
        "routes": [{"prefix": p, "base_url": u} for p, u in app.state.routes],
        "docs": "/docs",
    }


@app.api_route("/api/{path:path}", methods=_ALLOWED_METHODS)
async def proxy_api(request: Request, path: str):
    # full path including /api prefix
    full_path = request.url.path

    base_url = _match_backend(full_path, app.state.routes)
    if not base_url:
        return JSONResponse(
            status_code=404,
            content={
                "detail": "No route for path",
                "path": full_path,
                "knownPrefixes": [p for p, _ in app.state.routes],
            },
        )

    target_url = f"{base_url}{full_path}"

    body = await request.body()
    headers = _filtered_headers(request.headers.items())

    # Use raw query string to preserve repeated params etc.
    query = request.url.query
    if query:
        target_url = f"{target_url}?{query}"

    timeout_override = app.state.timeout_chat if full_path.startswith("/api/v1/chat") else app.state.timeout_default

    try:
        upstream = await app.state.http.request(
            request.method,
            target_url,
            content=body,
            headers=headers,
            timeout=timeout_override,
        )
    except httpx.TimeoutException:
        return JSONResponse(status_code=504, content={"detail": "Upstream timeout"})
    except httpx.RequestError as e:
        return JSONResponse(status_code=502, content={"detail": "Upstream error", "error": str(e)})

    resp_headers = _filtered_headers(upstream.headers.items())
    media_type = upstream.headers.get("content-type")

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=resp_headers,
        media_type=media_type,
    )
