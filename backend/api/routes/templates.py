"""Template routes — custom template uploads, compile lifecycle, and previews.

Endpoints (all under ``/api/templates``):

- ``POST   /upload``                    Multipart upload + dispatch async
                                        compile. Returns ``ACCEPTED`` with
                                        the COMPILING record.
- ``GET    ""``                         List all templates (inbuilt are
                                        served separately by the frontend
                                        constants — only customs live in
                                        this repository).
- ``GET    /{id}``                      Full record. Returns ``202`` with
                                        a minimal payload while the
                                        template is still compiling so
                                        the UI can poll without a 404.
- ``GET    /{id}/compile-status``       Just the status + last error,
                                        used by the templates page poll.
- ``GET    /{id}/schema``               Compiled placeholder schema.
- ``POST   /{id}/validate``             Re-extract and validate the
                                        schema on demand.
- ``PATCH  /{id}/bindings``             Replace the section -> placeholder
                                        binding map.
- ``POST   /{id}/recompile``            Reset to COMPILING and re-run.
- ``GET    /{id}/fidelity-report``      Fidelity issues and summary;
                                        ``?refresh=true`` re-runs the
                                        probe.
- ``GET    /{id}/download``             Original uploaded file.
- ``GET    /{id}/preview-binary``       Generated DOCX preview file.
- ``GET    /{id}/preview-html``         XLSX-only HTML preview.
- ``DELETE /{id}``                      Remove the record and on-disk files.

Validation note: PDD/SDD templates must be ``.docx`` and UAT must be
``.xlsx``. Anything else fails fast at upload with a 400.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse

from api.deps import get_task_dispatcher, get_template_service
from core.constants import DocType, TemplateStatus
from core.exceptions import TemplateException, ValidationException
from core.logging import get_logger, verbose_logs_enabled
from core.response import created_response, success_response
from services.template_service import TemplateService

router = APIRouter()
logger = get_logger(__name__)


@router.post("/upload")
async def upload_template(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    template_type: str = Form(...),
    version: str | None = Form(None),
    template_service: TemplateService = Depends(get_template_service),
    task_dispatcher=Depends(get_task_dispatcher),
) -> object:
    logger.info(
        "templates.upload.request filename=%s template_type=%s version=%s",
        file.filename,
        template_type,
        version,
    )

    try:
        normalized_type = DocType(template_type).value
    except ValueError as exc:
        raise ValidationException(f"Invalid template_type: {template_type}") from exc
    filename = file.filename or "template.bin"
    suffix = Path(filename).suffix.lower()
    expected_suffix = ".xlsx" if normalized_type == DocType.UAT.value else ".docx"
    if suffix != expected_suffix:
        raise ValidationException(
            f"Invalid template file for {normalized_type}. Expected {expected_suffix} but got {suffix or 'no extension'}."
        )

    payload = await file.read()
    if verbose_logs_enabled():
        logger.info("templates.upload.measured payload_bytes=%s", len(payload))

    record = template_service.save_template(
        filename=filename,
        template_type=normalized_type,
        payload=payload,
        version=version,
    )

    task_dispatcher.dispatch(background_tasks, template_service.compile_template, record.template_id)

    logger.info(
        "templates.upload.completed template_id=%s status=%s",
        record.template_id,
        record.status,
    )
    return created_response(record.model_dump(), message="Template accepted")


@router.get("")
async def list_templates(
    template_service: TemplateService = Depends(get_template_service),
) -> object:
    logger.info("templates.list.started")
    items = [item.model_dump() for item in template_service.list_all()]
    logger.info("templates.list.completed total=%s", len(items))
    return success_response({"items": items, "total": len(items)})


@router.get("/{template_id}")
async def get_template(
    template_id: str,
    template_service: TemplateService = Depends(get_template_service),
) -> object:
    logger.info("templates.get.started template_id=%s", template_id)

    record = template_service.get_or_raise(template_id)

    if record.status in {TemplateStatus.COMPILING.value, TemplateStatus.PENDING.value}:
        logger.info(
            "templates.get.pending template_id=%s status=%s",
            template_id,
            record.status,
        )
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content=_pending_template_payload(record),
        )

    logger.info(
        "templates.get.completed template_id=%s status=%s",
        template_id,
        record.status,
    )
    payload = record.model_dump()
    payload["export_path_hint"] = template_service.export_path_hint_for_record(record)
    return success_response(data=payload)


@router.get("/{template_id}/compile-status")
async def get_compile_status(
    template_id: str,
    template_service: TemplateService = Depends(get_template_service),
) -> object:
    logger.info("templates.compile.started template_id=%s", template_id)

    record = template_service.get_or_raise(template_id)
    data = {
        "template_id": record.template_id,
        "status": record.status,
        "error": record.compile_error,
        "compiled_at": record.compiled_at,
        "section_count": len(record.section_plan),
        "sheet_map": record.sheet_map,
    }

    logger.info(
        "templates.compile.completed template_id=%s status=%s",
        template_id,
        record.status,
    )
    return success_response(data)


@router.get("/{template_id}/schema")
async def get_template_schema(
    template_id: str,
    template_service: TemplateService = Depends(get_template_service),
) -> object:
    record = template_service.get_or_raise(template_id)
    return success_response(
        {
            "template_id": record.template_id,
            "schema_version": record.schema_version,
            "validation_status": record.validation_status,
            "placeholder_schema": record.placeholder_schema,
        }
    )


@router.post("/{template_id}/validate")
async def validate_template_contract(
    template_id: str,
    template_service: TemplateService = Depends(get_template_service),
) -> object:
    result = template_service.validate_template_contract(template_id, persist=True)
    return success_response(result)


@router.patch("/{template_id}/bindings")
async def patch_template_bindings(
    template_id: str,
    body: dict[str, Any],
    template_service: TemplateService = Depends(get_template_service),
) -> object:
    """Replace explicit section_id → placeholder_id(s) map (JSON object body)."""
    record = template_service.update_section_bindings(template_id, body)
    return success_response(record.model_dump())


@router.post("/{template_id}/recompile")
async def recompile_template(
    template_id: str,
    background_tasks: BackgroundTasks,
    template_service: TemplateService = Depends(get_template_service),
    task_dispatcher=Depends(get_task_dispatcher),
) -> object:
    """Reset template to COMPILING and run compile again (idempotent queue)."""
    record = template_service.requeue_compile(template_id)
    task_dispatcher.dispatch(background_tasks, template_service.compile_template, record.template_id)
    payload = record.model_dump()
    payload["export_path_hint"] = template_service.export_path_hint_for_record(record)
    return success_response(payload, message="Template recompile queued")


@router.get("/{template_id}/fidelity-report")
async def get_template_fidelity_report(
    template_id: str,
    refresh: bool = False,
    template_service: TemplateService = Depends(get_template_service),
) -> object:
    if refresh:
        try:
            data = template_service.refresh_template_fidelity(template_id, persist=True)
        except TemplateException as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            ) from exc
        return success_response(data)

    record = template_service.get_or_raise(template_id)
    return success_response(template_service.fidelity_report(record))


@router.get("/{template_id}/download")
async def download_template(
    template_id: str,
    template_service: TemplateService = Depends(get_template_service),
):
    logger.info("templates.download.started template_id=%s", template_id)

    record = template_service.get_or_raise(template_id)

    if record.status != TemplateStatus.READY.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Template {template_id} is not ready for download. Current status: {record.status}",
        )

    file_path = template_service.get_file_path(template_id)

    logger.info(
        "templates.download.completed template_id=%s path=%s",
        template_id,
        str(file_path),
    )
    return FileResponse(
        path=file_path,
        filename=record.filename,
        media_type="application/octet-stream",
    )


@router.get("/{template_id}/preview-binary")
async def download_template_preview_binary(
    template_id: str,
    template_service: TemplateService = Depends(get_template_service),
):
    logger.info("templates.preview_binary.started template_id=%s", template_id)

    record = template_service.get_or_raise(template_id)

    if record.status != TemplateStatus.READY.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Template {template_id} is not ready for preview. Current status: {record.status}",
        )

    file_path = template_service.get_preview_file_path(template_id)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preview artifact missing for template {template_id}.",
        )

    logger.info(
        "templates.preview_binary.completed template_id=%s path=%s",
        template_id,
        str(file_path),
    )
    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@router.get("/{template_id}/preview-html")
async def get_preview_html(
    template_id: str,
    template_service: TemplateService = Depends(get_template_service),
) -> object:
    logger.info("templates.preview.started template_id=%s", template_id)

    record = template_service.get_or_raise(template_id)
    html = template_service.get_preview_html(template_id)
    if verbose_logs_enabled():
        logger.info(
            "templates.preview.completed template_id=%s html_bytes=%s",
            template_id,
            len(html.encode("utf-8")),
        )

    return success_response({"html": html, "sheet_map": record.sheet_map})


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    template_service: TemplateService = Depends(get_template_service),
) -> object:
    logger.info("templates.delete.started template_id=%s", template_id)

    template_service.delete(template_id)

    logger.info("templates.delete.completed template_id=%s", template_id)
    return success_response({"template_id": template_id}, message="Template deleted")


def _pending_template_payload(record) -> dict:
    """
    Minimal plain JSON payload while template compilation is still in progress.

    IMPORTANT:
    This must return a plain dict, not success_response(...), because get_template()
    wraps it with JSONResponse(..., status_code=202).
    """
    return {
        "success": True,
        "message": "Template is still compiling.",
        "data": {
            "template_id": record.template_id,
            "filename": record.filename,
            "template_type": record.template_type,
            "version": record.version,
            "status": record.status,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
            "compiled_at": getattr(record, "compiled_at", None),
            "preview_path": None,
            "preview_html": None,
            "section_plan": [],
            "style_map": None,
            "sheet_map": {},
            "compile_error": None,
        },
    }
