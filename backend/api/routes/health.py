"""Health and readiness probes.

Two endpoints:

- ``GET /api/health``  Cheap liveness check used by container orchestrators.
                       Returns ``{"status": "ok"}`` and never inspects
                       external state.

- ``GET /api/ready``   Readiness probe. Verifies that ``storage_root`` is
                       writable and (in non-local environments) that the
                       three Azure services are configured. Returns 503
                       with a list of failed checks when any check fails
                       so the orchestrator can withhold traffic.
"""

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
    storage_writable = verify_storage_writable(settings.storage_root)
    failed_checks: list[str] = []
    if not storage_writable:
        failed_checks.append("storage_writable")

    azure_openai_configured = bool(settings.azure_openai_endpoint and settings.azure_openai_api_key)
    azure_search_configured = bool(settings.azure_search_endpoint and settings.azure_search_api_key)
    azure_doc_intelligence_configured = bool(
        settings.azure_document_intelligence_endpoint and settings.azure_document_intelligence_key
    )
    if not settings.is_local_env():
        if not azure_openai_configured:
            failed_checks.append("azure_openai_configured")
        if not azure_search_configured:
            failed_checks.append("azure_search_configured")
        if not azure_doc_intelligence_configured:
            failed_checks.append("azure_doc_intelligence_configured")

    critical_checks_passed = len(failed_checks) == 0
    status = "ready" if critical_checks_passed else "not_ready"
    data = {
        "status": status,
        "app": settings.app_name,
        "env": settings.app_env,
        "azure_openai_configured": azure_openai_configured,
        "azure_search_configured": azure_search_configured,
        "azure_doc_intelligence_configured": azure_doc_intelligence_configured,
        "kroki_url": settings.kroki_url,
        "storage_root": str(settings.storage_root),
        "storage_writable": storage_writable,
        "critical_checks_passed": critical_checks_passed,
        "failed_checks": failed_checks,
    }
    logger.info(
        "ready.check.completed status=%s env=%s storage_writable=%s failed_checks=%s",
        data["status"],
        data["env"],
        data["storage_writable"],
        failed_checks,
    )
    status_code = 200 if critical_checks_passed else 503
    return success_response(data, status_code=status_code)
