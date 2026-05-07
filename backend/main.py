"""FastAPI application entrypoint for the backend."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.router import api_router
from core.config import ensure_storage_dirs, settings
from core.exceptions import NotFoundException, SDLCBaseException
from core.hosting import run_hosting_startup
from core.logging import configure_logging
from core.response import error_response

from core.logging import get_logger

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
        logger.exception("unhandled_exception error=%s", str(exc))
        detail = "An unexpected error occurred."
        if settings.app_debug and settings.is_local_env():
            detail = str(exc)
        return error_response(
            message="Internal server error",
            errors=[{"code": "INTERNAL_ERROR", "detail": detail}],
            status_code=500,
        )

    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
