"""FastAPI application entrypoint for the backend."""

from __future__ import annotations

from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.router import api_router
from core.config import ensure_storage_dirs, settings
from core.exceptions import NotFoundException, SDLCBaseException
from core.hosting import run_hosting_startup
from core.logging import configure_logging, get_logger, verbose_logs_enabled
from core.response import error_response

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    ensure_storage_dirs()
    run_hosting_startup(settings)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=settings.app_debug, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list(),
        allow_credentials=settings.cors_allow_credentials(),
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_trace_middleware(request: Request, call_next):
        if not verbose_logs_enabled():
            return await call_next(request)

        request_id = str(uuid4())
        started_at = perf_counter()
        body_text = ""
        try:
            raw_body = await request.body()
            body_text = raw_body.decode("utf-8", errors="replace")
        except Exception:
            body_text = "<unavailable>"

        logger.info(
            "request.started request_id=%s method=%s path=%s query=%s body=%s",
            request_id,
            request.method,
            request.url.path,
            dict(request.query_params),
            body_text[:2000],
        )
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "request.failed request_id=%s method=%s path=%s",
                request_id,
                request.method,
                request.url.path,
            )
            raise

        duration_ms = int((perf_counter() - started_at) * 1000)
        logger.info(
            "request.completed request_id=%s method=%s path=%s status_code=%s duration_ms=%s",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response

    @app.exception_handler(NotFoundException)
    async def handle_not_found(_: Request, exc: NotFoundException) -> JSONResponse:
        return error_response(
            message=exc.message,
            errors=[{"code": exc.code, "detail": exc.message}],
            status_code=404,
        )

    @app.exception_handler(SDLCBaseException)
    async def handle_sdlc_error(_: Request, exc: SDLCBaseException) -> JSONResponse:
        return error_response(
            message=exc.message,
            errors=[{"code": exc.code, "detail": exc.message}],
            status_code=400,
        )

    @app.exception_handler(Exception)
    async def handle_internal_error(_: Request, exc: Exception) -> JSONResponse:
        return error_response(
            message="Internal server error",
            errors=[{"code": "INTERNAL_ERROR", "detail": str(exc)}],
            status_code=500,
        )

    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
