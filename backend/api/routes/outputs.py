"""Output routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from api.deps import get_output_service
from core.response import success_response
from services.output_service import OutputService

router = APIRouter()


@router.get("/{output_id}")
async def get_output(output_id: str, output_service: OutputService = Depends(get_output_service)) -> object:
    output = output_service.get_or_raise(output_id)
    return success_response(output.model_dump())


@router.get("/{output_id}/download")
async def download_output(output_id: str, output_service: OutputService = Depends(get_output_service)) -> FileResponse:
    path, filename = output_service.get_download_info(output_id)
    return FileResponse(path=path, filename=filename, media_type="application/octet-stream")
