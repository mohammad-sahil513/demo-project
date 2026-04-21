"""Central API router."""

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
