"""FastAPI application entrypoint for the AI SDLC backend.

This module is the single composition root for the backend service. It wires
together application configuration, structured logging, the request/response
envelope contract, exception-to-HTTP mapping, CORS, and the public API router.

Responsibilities
----------------
- Build the :class:`fastapi.FastAPI` instance via :func:`create_app`.
- Configure logging and ensure storage directories exist exactly once on
  startup (FastAPI lifespan).
- Run production-only hosting checks (strict-mode validation, storage probe,
  reconciliation of workflows that were ``RUNNING`` when the process died).
- Map domain exceptions (:class:`core.exceptions.SDLCBaseException` family)
  onto the standard JSON envelope from :mod:`core.response`, so the frontend
  always receives a uniform shape (``success/message/data/errors/meta``).

Layering
--------
``main.py`` is allowed to import from every layer (``api``, ``core``) because
it is the application entrypoint. No business logic must live here — only
composition and cross-cutting concerns (CORS, error mapping, lifespan).

Related docs
------------
- ``docs/ARCHITECTURE.md`` — full backend file catalog and layer overview.
- ``docs/ARCHITECTURE.md`` — high-level system overview and structure.
- ``docs/API.md`` — public HTTP contract.
"""

from __future__ import annotations

# ``contextlib.asynccontextmanager`` is required to use a function-based
# lifespan handler. Anything before the ``yield`` runs at startup, anything
# after runs at shutdown.
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Public HTTP surface lives in ``api/router.py``; importing here is the
# composition step that turns the routes into a mountable router.
from api.router import api_router
from core.config import ensure_storage_dirs, settings
from core.exceptions import NotFoundException, SDLCBaseException
from core.hosting import run_hosting_startup
from core.logging import configure_logging
from core.response import error_response

# Logger import is duplicated intentionally to keep ``get_logger`` close to the
# place where the module-level logger is constructed; ``configure_logging`` is
# invoked from the lifespan, while ``get_logger`` produces a named instance
# suitable for use before logging is fully configured (it will pick up handlers
# once ``configure_logging`` runs).
from core.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """FastAPI lifespan hook — runs once on startup and once on shutdown.

    Order matters: logging must be configured before any other startup step so
    that subsequent log lines (storage init, hosting probes, workflow
    reconciliation) are routed through the configured handlers and filters.
    """
    # 1) Wire structured logging (console + per-workflow file sinks).
    configure_logging()
    # 2) Make sure ``storage/<documents|templates|workflows|outputs|...>``
    #    directories exist so request handlers never have to create them.
    ensure_storage_dirs()
    # 3) Production-only safety net: validate strict env flags, verify the
    #    storage root is writable, prune old observability logs, and mark any
    #    ``RUNNING`` workflows as ``FAILED`` (background tasks do not survive
    #    a process restart on FastAPI BackgroundTasks).
    run_hosting_startup(settings)
    # ``yield`` hands control to the application. Anything after this point
    # would run on shutdown — currently we have nothing to clean up.
    yield


def create_app() -> FastAPI:
    """Build and return the :class:`FastAPI` application instance.

    This is a factory (not a singleton) so that tests can construct an app
    with overridden settings; the module-level ``app`` variable below is the
    default instance used by the ASGI server (``uvicorn main:app``).
    """
    app = FastAPI(title=settings.app_name, debug=settings.app_debug, lifespan=lifespan)

    # CORS is configured from ``settings.cors_origins`` (comma-separated). The
    # helper enforces the browser rule that ``*`` origin and credentialed
    # requests are mutually exclusive — see ``core.config.Settings``.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list(),
        allow_credentials=settings.cors_allow_credentials(),
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Exception handlers ------------------------------------------------
    # The handler order does not matter — FastAPI matches by exception type,
    # most-specific first. We register the narrowest first for readability.

    @app.exception_handler(NotFoundException)
    async def handle_not_found(_: Request, exc: NotFoundException) -> JSONResponse:
        # 404 is returned for missing resources (documents, templates, runs).
        # ``error_response`` always returns the standard envelope shape that
        # the frontend Axios interceptor expects (see ``frontend/src/api/client.ts``).
        return error_response(
            message=exc.message,
            errors=[{"code": exc.code, "detail": exc.message}],
            status_code=404,
        )

    @app.exception_handler(SDLCBaseException)
    async def handle_sdlc_error(_: Request, exc: SDLCBaseException) -> JSONResponse:
        # All domain errors (validation, workflow, ingestion, template, etc.)
        # come through as 400 Bad Request with the exception's machine code.
        # Status 400 keeps the response shape simple — callers should inspect
        # ``errors[0].code`` to differentiate causes.
        return error_response(
            message=exc.message,
            errors=[{"code": exc.code, "detail": exc.message}],
            status_code=400,
        )

    @app.exception_handler(Exception)
    async def handle_internal_error(_: Request, exc: Exception) -> JSONResponse:
        # Catch-all for unanticipated errors. We always log the stack trace
        # (``logger.exception`` captures ``__traceback__``) and only leak the
        # exception ``str()`` to the client in local development; production
        # responses receive a generic message to avoid information disclosure.
        logger.exception("unhandled_exception error=%s", str(exc))
        detail = "An unexpected error occurred."
        if settings.app_debug and settings.is_local_env():
            detail = str(exc)
        return error_response(
            message="Internal server error",
            errors=[{"code": "INTERNAL_ERROR", "detail": detail}],
            status_code=500,
        )

    # Mount the API under the configurable prefix (``/api`` by default). The
    # frontend dev proxy and production rewrites assume this prefix.
    app.include_router(api_router, prefix=settings.api_prefix)
    return app


# Module-level ASGI application — ``uvicorn main:app`` and the production
# hosting platform import this name directly.
app = create_app()
