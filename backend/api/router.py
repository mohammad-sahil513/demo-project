"""Central API router — composes every feature sub-router under one mount.

:data:`api_router` is included by :func:`main.create_app` under the
``/api`` prefix. Adding a new feature is a two-step process:

1. Create the route module under :mod:`api.routes`.
2. Append a single ``include_router`` call here with the resource prefix
   and OpenAPI tag.

The order below is incidental — FastAPI does not require any specific
ordering, but grouping related resources next to each other keeps the
generated OpenAPI document tidy.
"""

from __future__ import annotations

from fastapi import APIRouter

from api.routes import documents, events, health, outputs, templates, workflows

api_router = APIRouter()
api_router.include_router(health.router, prefix="", tags=["health"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(workflows.router, prefix="/workflow-runs", tags=["workflow-runs"])
api_router.include_router(outputs.router, prefix="/outputs", tags=["outputs"])
api_router.include_router(events.router, prefix="/workflow-runs", tags=["events"])
