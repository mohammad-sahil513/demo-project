"""Document routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile

from core.response import created_response, success_response
from services.document_service import DocumentService

from api.deps import get_document_service

router = APIRouter()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_service: DocumentService = Depends(get_document_service),
) -> object:
    payload = await file.read()
    record = document_service.save_document(
        filename=file.filename or "uploaded.bin",
        content_type=file.content_type or "application/octet-stream",
        payload=payload,
    )
    return created_response(record.model_dump(), message="Document uploaded")


@router.get("")
async def list_documents(document_service: DocumentService = Depends(get_document_service)) -> object:
    items = [item.model_dump() for item in document_service.list_all()]
    return success_response({"items": items, "total": len(items)})


@router.get("/{document_id}")
async def get_document(document_id: str, document_service: DocumentService = Depends(get_document_service)) -> object:
    record = document_service.get_or_raise(document_id)
    return success_response(record.model_dump())


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service),
) -> object:
    document_service.delete(document_id)
    return success_response({"document_id": document_id}, message="Document deleted")
