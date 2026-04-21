"""Health and readiness routes."""

from __future__ import annotations

from fastapi import APIRouter

from core.config import settings
from core.hosting import verify_storage_writable
from core.logging import get_logger
from core.response import success_response

router = APIRouter()
logger = get_logger(__name__)


@router.get("/health")
async def health() -> object:
    logger.info("health.check.started")
    return success_response({"status": "ok"})


@router.get("/ready")
async def ready() -> object:
    logger.info("ready.check.started")
    data = {
        "status": "ready",
        "app": settings.app_name,
        "env": settings.app_env,
        "azure_openai_configured": bool(settings.azure_openai_endpoint),
        "azure_search_configured": bool(settings.azure_search_endpoint),
        "azure_doc_intelligence_configured": bool(settings.azure_document_intelligence_endpoint),
        "kroki_url": settings.kroki_url,
        "storage_root": str(settings.storage_root),
        "storage_writable": verify_storage_writable(settings.storage_root),
    }
    logger.info(
        "ready.check.completed status=%s env=%s storage_writable=%s",
        data["status"],
        data["env"],
        data["storage_writable"],
    )
    return success_response(data)
