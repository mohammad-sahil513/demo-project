"""Document routes — BRD uploads, listing, retrieval, deletion, and cost view.

Endpoints (all under ``/api/documents`` prefix):

- ``POST /upload``        Multipart upload of a single BRD (PDF/DOCX).
                          The server stores the binary and registers a
                          :class:`DocumentRecord`. Ingestion does NOT
                          run here — it runs on demand in the workflow
                          ingest phase.
- ``GET  ""``             List every document in the storage root.
- ``GET  /{id}``          One record plus its aggregated cost summary.
- ``GET  /{id}/cost``     Just the cost summary (cheaper than ``/{id}``).
- ``DELETE /{id}``        Refuses while any workflow against the doc is
                          RUNNING — see ``ensure_document_safe_to_delete``.

All responses use the standard JSON envelope from :mod:`core.response`.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile

from core.logging import get_logger, verbose_logs_enabled
from core.response import created_response, success_response
from services.document_service import DocumentService

from api.deps import get_document_service

router = APIRouter()
logger = get_logger(__name__)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_service: DocumentService = Depends(get_document_service),
) -> object:
    payload = await file.read()
    logger.info(
        "documents.upload.request filename=%s content_type=%s payload_bytes=%s",
        file.filename,
        file.content_type,
        len(payload),
    )
    record = document_service.save_document(
        filename=file.filename or "uploaded.bin",
        content_type=file.content_type or "application/octet-stream",
        payload=payload,
    )
    logger.info("documents.upload.completed document_id=%s", record.document_id)
    return created_response(record.model_dump(), message="Document uploaded")


@router.get("")
async def list_documents(document_service: DocumentService = Depends(get_document_service)) -> object:
    logger.info("documents.list.started")
    items = [item.model_dump() for item in document_service.list_all()]
    logger.info("documents.list.completed total=%s", len(items))
    return success_response({"items": items, "total": len(items)})


@router.get("/{document_id}")
async def get_document(document_id: str, document_service: DocumentService = Depends(get_document_service)) -> object:
    logger.info("documents.get.started document_id=%s", document_id)
    record = document_service.get_or_raise(document_id)
    payload = record.model_dump()
    payload["cost_summary"] = document_service.cost_summary(document_id)
    if verbose_logs_enabled():
        logger.info("documents.get.completed document_id=%s filename=%s", document_id, record.filename)
    return success_response(payload)


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service),
) -> object:
    logger.info("documents.delete.started document_id=%s", document_id)
    document_service.delete(document_id)
    logger.info("documents.delete.completed document_id=%s", document_id)
    return success_response({"document_id": document_id}, message="Document deleted")


@router.get("/{document_id}/cost")
async def get_document_cost(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service),
) -> object:
    logger.info("documents.cost.started document_id=%s", document_id)
    document_service.get_or_raise(document_id)
    data = document_service.cost_summary(document_id)
    logger.info(
        "documents.cost.completed document_id=%s workflow_count=%s total_cost_usd=%s",
        document_id,
        data.get("workflow_count", 0),
        data.get("total_cost_usd", 0.0),
    )
    return success_response(data)
