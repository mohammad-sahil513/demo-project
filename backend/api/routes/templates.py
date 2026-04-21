"""Template routes."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse

from core.constants import DocType
from core.exceptions import ValidationException
from core.response import created_response, success_response
from services.template_service import TemplateService

from api.deps import get_task_dispatcher, get_template_service

router = APIRouter()


@router.post("/upload")
async def upload_template(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    template_type: str = Form(...),
    version: str | None = Form(None),
    template_service: TemplateService = Depends(get_template_service),
    task_dispatcher=Depends(get_task_dispatcher),
) -> object:
    try:
        normalized_type = DocType(template_type).value
    except ValueError as exc:
        raise ValidationException(f"Invalid template_type: {template_type}") from exc

    payload = await file.read()
    record = template_service.save_template(
        filename=file.filename or "template.bin",
        template_type=normalized_type,
        payload=payload,
        version=version,
    )
    task_dispatcher.dispatch(background_tasks, template_service.compile_template, record.template_id)
    return created_response(record.model_dump(), message="Template accepted")


@router.get("")
async def list_templates(template_service: TemplateService = Depends(get_template_service)) -> object:
    items = [item.model_dump() for item in template_service.list_all()]
    return success_response({"items": items, "total": len(items)})


@router.get("/{template_id}")
async def get_template(template_id: str, template_service: TemplateService = Depends(get_template_service)) -> object:
    record = template_service.get_or_raise(template_id)
    return success_response(record.model_dump())


@router.get("/{template_id}/compile-status")
async def get_compile_status(
    template_id: str,
    template_service: TemplateService = Depends(get_template_service),
) -> object:
    record = template_service.get_or_raise(template_id)
    data = {
        "template_id": record.template_id,
        "status": record.status,
        "error": record.compile_error,
        "compiled_at": record.compiled_at,
        "section_count": len(record.section_plan),
    }
    return success_response(data)


@router.get("/{template_id}/download")
async def download_template(
    template_id: str,
    template_service: TemplateService = Depends(get_template_service),
) -> FileResponse:
    file_path = template_service.get_file_path(template_id)
    return FileResponse(path=file_path, filename=file_path.name, media_type="application/octet-stream")


@router.get("/{template_id}/preview-html")
async def get_preview_html(
    template_id: str,
    template_service: TemplateService = Depends(get_template_service),
) -> object:
    html = template_service.get_preview_html(template_id)
    return success_response({"html": html})


@router.delete("/{template_id}")
async def delete_template(template_id: str, template_service: TemplateService = Depends(get_template_service)) -> object:
    template_service.delete(template_id)
    return success_response({"template_id": template_id}, message="Template deleted")
