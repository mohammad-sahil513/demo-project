"""Output routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from api.deps import get_output_service
from core.logging import get_logger, verbose_logs_enabled
from core.response import success_response
from services.output_service import OutputService

router = APIRouter()
logger = get_logger(__name__)


@router.get("/{output_id}")
async def get_output(output_id: str, output_service: OutputService = Depends(get_output_service)) -> object:
    logger.info("outputs.get.started output_id=%s", output_id)
    output = output_service.get_or_raise(output_id)
    if verbose_logs_enabled():
        logger.info(
            "outputs.get.completed output_id=%s workflow_run_id=%s filename=%s",
            output_id,
            output.workflow_run_id,
            output.filename,
        )
    return success_response(output.model_dump())


@router.get("/{output_id}/download")
async def download_output(output_id: str, output_service: OutputService = Depends(get_output_service)) -> FileResponse:
    logger.info("outputs.download.started output_id=%s", output_id)
    path, filename = output_service.get_download_info(output_id)
    logger.info("outputs.download.completed output_id=%s path=%s filename=%s", output_id, path, filename)
    return FileResponse(path=path, filename=filename, media_type="application/octet-stream")
