# Project Context Export

Generated on: `2026-04-30 10:41:36`

## Included Roots

- `C:\Office Stuff\PROJECT\demo-project\backend`

## Folder Structure

### Root: `backend`

```text
backend
├── api
│   ├── routes
│   │   ├── __init__.py
│   │   ├── documents.py
│   │   ├── events.py
│   │   ├── health.py
│   │   ├── outputs.py
│   │   ├── templates.py
│   │   └── workflows.py
│   ├── __init__.py
│   ├── deps.py
│   └── router.py
├── core
│   ├── __init__.py
│   ├── config.py
│   ├── constants.py
│   ├── exceptions.py
│   ├── hosting.py
│   ├── ids.py
│   ├── logging.py
│   ├── response.py
│   └── token_count.py
├── infrastructure
│   ├── __init__.py
│   ├── doc_intelligence.py
│   ├── search_client.py
│   └── sk_adapter.py
├── modules
│   ├── assembly
│   │   ├── __init__.py
│   │   ├── assembler.py
│   │   ├── models.py
│   │   └── normalizer.py
│   ├── export
│   │   ├── __init__.py
│   │   ├── content_blocks.py
│   │   ├── docx_builder.py
│   │   ├── docx_filler.py
│   │   ├── markdown_tables.py
│   │   ├── renderer.py
│   │   ├── types.py
│   │   └── xlsx_builder.py
│   ├── generation
│   │   ├── __init__.py
│   │   ├── context.py
│   │   ├── cost_tracking.py
│   │   ├── diagram_generator.py
│   │   ├── kroki.py
│   │   ├── models.py
│   │   ├── observability.py
│   │   ├── orchestrator.py
│   │   ├── prompt_loader.py
│   │   ├── table_generator.py
│   │   └── text_generator.py
│   ├── ingestion
│   │   ├── __init__.py
│   │   ├── chunker.py
│   │   ├── indexer.py
│   │   ├── ingestion_coordinator.py
│   │   ├── orchestrator.py
│   │   └── parser.py
│   ├── observability
│   │   ├── __init__.py
│   │   └── cost_rollup.py
│   ├── retrieval
│   │   ├── __init__.py
│   │   ├── packager.py
│   │   └── retriever.py
│   ├── template
│   │   ├── inbuilt
│   │   │   ├── styles
│   │   │   │   ├── __init__.py
│   │   │   │   ├── pdd_style.py
│   │   │   │   ├── sdd_style.py
│   │   │   │   └── uat_style.py
│   │   │   ├── __init__.py
│   │   │   ├── pdd_sections.py
│   │   │   ├── registry.py
│   │   │   ├── sdd_sections.py
│   │   │   └── uat_sections.py
│   │   ├── __init__.py
│   │   ├── classifier.py
│   │   ├── extractor.py
│   │   ├── models.py
│   │   ├── planner.py
│   │   └── preview_generator.py
│   └── __init__.py
├── prompts
│   ├── generation
│   │   ├── diagram
│   │   │   ├── architecture.yaml
│   │   │   ├── correction.yaml
│   │   │   ├── default.yaml
│   │   │   ├── flowchart.yaml
│   │   │   ├── mermaid_default.yaml
│   │   │   └── sequence.yaml
│   │   ├── table
│   │   │   ├── api_specification.yaml
│   │   │   ├── default.yaml
│   │   │   ├── risk_register.yaml
│   │   │   ├── stakeholders.yaml
│   │   │   └── traceability_matrix.yaml
│   │   └── text
│   │       ├── architecture.yaml
│   │       ├── assumptions.yaml
│   │       ├── default.yaml
│   │       ├── overview.yaml
│   │       ├── requirements.yaml
│   │       ├── risks.yaml
│   │       └── scope.yaml
│   └── template
│       └── classifier.yaml
├── repositories
│   ├── __init__.py
│   ├── base.py
│   ├── document_models.py
│   ├── document_repo.py
│   ├── output_models.py
│   ├── output_repo.py
│   ├── template_models.py
│   ├── template_repo.py
│   ├── workflow_models.py
│   └── workflow_repo.py
├── scripts
│   ├── ai_search_index.py
│   └── validate_ai_search_index.py
├── services
│   ├── __init__.py
│   ├── document_service.py
│   ├── event_service.py
│   ├── output_service.py
│   ├── policy.py
│   ├── template_service.py
│   ├── workflow_executor.py
│   └── workflow_service.py
├── tools
│   ├── repo_to_markdown.py
│   └── smoke_azure.py
├── workers
│   ├── __init__.py
│   └── dispatcher.py
├── .env
├── .env.example
├── main.py
├── pytest.ini
└── requirements.txt
```

## File Contents

### Files from `backend`

#### `backend/api/__init__.py`

**Language hint:** `python`

```python
"""API package."""
```

#### `backend/api/deps.py`

**Language hint:** `python`

```python
"""Dependency providers for API routes."""

from __future__ import annotations

from functools import lru_cache

from infrastructure.doc_intelligence import AzureDocIntelligenceClient
from infrastructure.search_client import AzureSearchClient
from infrastructure.sk_adapter import AzureSKAdapter
from modules.ingestion.chunker import DocumentChunker
from modules.ingestion.indexer import DocumentIndexer
from modules.ingestion.ingestion_coordinator import IngestionCoordinator
from modules.ingestion.orchestrator import IngestionOrchestrator
from modules.ingestion.parser import DocumentParser
from modules.generation.diagram_generator import DiagramSectionGenerator
from modules.generation.kroki import KrokiRenderer
from modules.generation.orchestrator import GenerationOrchestrator
from modules.generation.table_generator import TableSectionGenerator
from modules.generation.text_generator import TextSectionGenerator
from modules.retrieval.packager import EvidencePackager
from modules.retrieval.retriever import SectionRetriever
from modules.template.classifier import TemplateClassifier
from modules.template.extractor import TemplateExtractor
from modules.template.planner import SectionPlanner
from modules.template.preview_generator import TemplatePreviewGenerator
from repositories.document_repo import DocumentRepository
from repositories.output_repo import OutputRepository
from repositories.template_repo import TemplateRepository
from repositories.workflow_repo import WorkflowRepository
from services.document_service import DocumentService
from services.event_service import EventService
from services.output_service import OutputService
from services.template_service import TemplateService
from services.workflow_executor import WorkflowExecutor
from services.workflow_service import WorkflowService
from workers.dispatcher import TaskDispatcher

from core.config import settings

# Module-level singletons (must not be recreated per request).
event_service_singleton = EventService()
task_dispatcher_singleton = TaskDispatcher()


def get_document_repository() -> DocumentRepository:
    return DocumentRepository(settings.documents_path)


def get_template_repository() -> TemplateRepository:
    return TemplateRepository(settings.templates_path)


def get_workflow_repository() -> WorkflowRepository:
    return WorkflowRepository(settings.workflows_path)


def get_output_repository() -> OutputRepository:
    return OutputRepository(settings.outputs_path)


def get_document_service() -> DocumentService:
    return DocumentService(
        get_document_repository(),
        workflow_repo=get_workflow_repository(),
    )


def get_template_service() -> TemplateService:
    return TemplateService(
        get_template_repository(),
        extractor=get_template_extractor(),
        classifier=get_template_classifier(),
        planner=get_section_planner(),
        preview_generator=get_template_preview_generator(),
        sk_adapter=get_sk_adapter(),
    )


def get_workflow_service() -> WorkflowService:
    return WorkflowService(
        get_workflow_repository(),
        document_repo=get_document_repository(),
        template_repo=get_template_repository(),
    )


def get_output_service() -> OutputService:
    return OutputService(get_output_repository())


def get_event_service() -> EventService:
    return event_service_singleton


def get_task_dispatcher() -> TaskDispatcher:
    return task_dispatcher_singleton


@lru_cache(maxsize=1)
def get_doc_intelligence_client() -> AzureDocIntelligenceClient:
    return AzureDocIntelligenceClient()


@lru_cache(maxsize=1)
def get_sk_adapter() -> AzureSKAdapter:
    return AzureSKAdapter()


@lru_cache(maxsize=1)
def get_search_client() -> AzureSearchClient:
    return AzureSearchClient()


@lru_cache(maxsize=1)
def get_ingestion_parser() -> DocumentParser:
    return DocumentParser(get_doc_intelligence_client())


@lru_cache(maxsize=1)
def get_document_chunker() -> DocumentChunker:
    return DocumentChunker(token_mode=settings.chunker_token_mode)


@lru_cache(maxsize=1)
def get_document_indexer() -> DocumentIndexer:
    return DocumentIndexer(search_client=get_search_client(), sk_adapter=get_sk_adapter())


@lru_cache(maxsize=1)
def get_ingestion_coordinator() -> IngestionCoordinator:
    return IngestionCoordinator(get_document_repository())


@lru_cache(maxsize=1)
def get_ingestion_orchestrator() -> IngestionOrchestrator:
    return IngestionOrchestrator(
        parser=get_ingestion_parser(),
        chunker=get_document_chunker(),
        indexer=get_document_indexer(),
        event_service=get_event_service(),
    )


@lru_cache(maxsize=1)
def get_section_retriever() -> SectionRetriever:
    return SectionRetriever(search_client=get_search_client(), sk_adapter=get_sk_adapter())


@lru_cache(maxsize=1)
def get_evidence_packager() -> EvidencePackager:
    return EvidencePackager()


@lru_cache(maxsize=1)
def get_generation_orchestrator() -> GenerationOrchestrator:
    sk = get_sk_adapter()
    return GenerationOrchestrator(
        text_generator=TextSectionGenerator(sk),
        table_generator=TableSectionGenerator(sk),
        diagram_generator=DiagramSectionGenerator(
            sk,
            kroki=KrokiRenderer(settings.kroki_url),
            storage_root=settings.storage_root,
        ),
    )


def get_workflow_executor() -> WorkflowExecutor:
    return WorkflowExecutor(
        workflow_service=get_workflow_service(),
        event_service=get_event_service(),
        ingestion_orchestrator=get_ingestion_orchestrator(),
        ingestion_coordinator=get_ingestion_coordinator(),
        section_retriever=get_section_retriever(),
        evidence_packager=get_evidence_packager(),
        generation_orchestrator=get_generation_orchestrator(),
        output_service=get_output_service(),
    )


@lru_cache(maxsize=1)
def get_template_extractor() -> TemplateExtractor:
    return TemplateExtractor()


@lru_cache(maxsize=1)
def get_template_classifier() -> TemplateClassifier:
    return TemplateClassifier(get_sk_adapter())


@lru_cache(maxsize=1)
def get_section_planner() -> SectionPlanner:
    return SectionPlanner()


@lru_cache(maxsize=1)
def get_template_preview_generator() -> TemplatePreviewGenerator:
    return TemplatePreviewGenerator()
```

#### `backend/api/router.py`

**Language hint:** `python`

```python
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
```

#### `backend/api/routes/__init__.py`

**Language hint:** `python`

```python
"""Route modules."""
```

#### `backend/api/routes/documents.py`

**Language hint:** `python`

```python
"""Document routes."""

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
    if verbose_logs_enabled():
        logger.info("documents.get.completed document_id=%s filename=%s", document_id, record.filename)
    return success_response(record.model_dump())


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service),
) -> object:
    logger.info("documents.delete.started document_id=%s", document_id)
    document_service.delete(document_id)
    logger.info("documents.delete.completed document_id=%s", document_id)
    return success_response({"document_id": document_id}, message="Document deleted")
```

#### `backend/api/routes/events.py`

**Language hint:** `python`

```python
"""SSE event route."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from api.deps import get_event_service
from core.logging import get_logger
from services.event_service import EventService

router = APIRouter()
logger = get_logger(__name__)


async def _event_stream(
    workflow_run_id: str,
    event_service: EventService,
) -> AsyncGenerator[str, None]:
    logger.info("events.stream.started workflow_run_id=%s", workflow_run_id)
    queue = event_service.subscribe(workflow_run_id)
    try:
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                logger.info(
                    "events.stream.event workflow_run_id=%s event_type=%s",
                    workflow_run_id,
                    event.get("type"),
                )
                yield f"data: {json.dumps(event)}\n\n"
                if event.get("type") in {"workflow.completed", "workflow.failed"}:
                    logger.info("events.stream.terminal workflow_run_id=%s", workflow_run_id)
                    break
            except asyncio.TimeoutError:
                logger.info("events.stream.heartbeat workflow_run_id=%s", workflow_run_id)
                yield ": heartbeat\n\n"
    finally:
        event_service.unsubscribe(workflow_run_id, queue)
        logger.info("events.stream.completed workflow_run_id=%s", workflow_run_id)


@router.get("/{workflow_run_id}/events")
async def stream_workflow_events(
    workflow_run_id: str,
    event_service: EventService = Depends(get_event_service),
) -> StreamingResponse:
    logger.info("events.route.started workflow_run_id=%s", workflow_run_id)
    return StreamingResponse(
        _event_stream(workflow_run_id, event_service),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
```

#### `backend/api/routes/health.py`

**Language hint:** `python`

```python
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
```

#### `backend/api/routes/outputs.py`

**Language hint:** `python`

```python
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
```

#### `backend/api/routes/templates.py`

**Language hint:** `python`

```python
"""Template routes."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse

from api.deps import get_task_dispatcher, get_template_service
from core.constants import DocType, TemplateStatus
from core.exceptions import ValidationException
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

    payload = await file.read()
    if verbose_logs_enabled():
        logger.info("templates.upload.measured payload_bytes=%s", len(payload))

    record = template_service.save_template(
        filename=file.filename or "template.bin",
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
    return success_response(data=record.model_dump())


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
    }

    logger.info(
        "templates.compile.completed template_id=%s status=%s",
        template_id,
        record.status,
    )
    return success_response(data)


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


@router.get("/{template_id}/preview-html")
async def get_preview_html(
    template_id: str,
    template_service: TemplateService = Depends(get_template_service),
) -> object:
    logger.info("templates.preview.started template_id=%s", template_id)

    html = template_service.get_preview_html(template_id)
    if verbose_logs_enabled():
        logger.info(
            "templates.preview.completed template_id=%s html_bytes=%s",
            template_id,
            len(html.encode("utf-8")),
        )

    return success_response({"html": html})


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
```

#### `backend/api/routes/workflows.py`

**Language hint:** `python`

```python
"""Workflow routes."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel, ConfigDict

from api.deps import get_task_dispatcher, get_workflow_executor, get_workflow_service
from core.logging import get_logger, verbose_logs_enabled
from core.response import created_response, success_response
from services.workflow_executor import WorkflowExecutor
from services.workflow_service import WorkflowService

router = APIRouter()
logger = get_logger(__name__)


class WorkflowCreateRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    document_id: str
    template_id: str
    doc_type: str | None = None
    start_immediately: bool = True


@router.post("")
async def create_workflow(
    payload: WorkflowCreateRequest,
    background_tasks: BackgroundTasks,
    workflow_service: WorkflowService = Depends(get_workflow_service),
    workflow_executor: WorkflowExecutor = Depends(get_workflow_executor),
    task_dispatcher=Depends(get_task_dispatcher),
) -> object:
    if verbose_logs_enabled():
        logger.info(
            "workflow.create.request document_id=%s template_id=%s doc_type=%s start_immediately=%s",
            payload.document_id,
            payload.template_id,
            payload.doc_type,
            payload.start_immediately,
        )
    record = workflow_service.create(
        document_id=payload.document_id,
        template_id=payload.template_id,
        doc_type=payload.doc_type,
    )
    if verbose_logs_enabled():
        logger.info("workflows.create.completed workflow_run_id=%s", record.workflow_run_id)
    if payload.start_immediately:
        if verbose_logs_enabled():
            logger.info("workflows.dispatch.started workflow_run_id=%s", record.workflow_run_id)
        task_dispatcher.dispatch(background_tasks, workflow_executor.run, record.workflow_run_id)
    return created_response(record.model_dump(), message="Workflow created")


@router.get("")
async def list_workflows(workflow_service: WorkflowService = Depends(get_workflow_service)) -> object:
    logger.info("workflows.list.started")
    items = [item.model_dump() for item in workflow_service.list_all()]
    logger.info("workflows.list.completed total=%s", len(items))
    return success_response({"items": items, "total": len(items)})


@router.get("/{workflow_run_id}")
async def get_workflow(
    workflow_run_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> object:
    logger.info("workflows.get.started workflow_run_id=%s", workflow_run_id)
    workflow = workflow_service.get_or_raise(workflow_run_id)
    if verbose_logs_enabled():
        logger.info(
            "workflows.get.completed workflow_run_id=%s status=%s phase=%s",
            workflow_run_id,
            workflow.status,
            workflow.current_phase,
        )
    return success_response(workflow.model_dump())


@router.get("/{workflow_run_id}/status")
async def get_workflow_status(
    workflow_run_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> object:
    logger.info("workflows.status.started workflow_run_id=%s", workflow_run_id)
    workflow = workflow_service.get_or_raise(workflow_run_id)
    data = {
        "workflow_run_id": workflow.workflow_run_id,
        "status": workflow.status,
        "current_phase": workflow.current_phase,
        "overall_progress_percent": workflow.overall_progress_percent,
        "current_step_label": workflow.current_step_label,
        "document_id": workflow.document_id,
        "template_id": workflow.template_id,
        "output_id": workflow.output_id,
    }
    logger.info(
        "workflows.status.completed workflow_run_id=%s status=%s progress=%s",
        workflow_run_id,
        workflow.status,
        workflow.overall_progress_percent,
    )
    return success_response(data)


@router.get("/{workflow_run_id}/sections")
async def get_workflow_sections(
    workflow_run_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> object:
    logger.info("workflows.sections.started workflow_run_id=%s", workflow_run_id)
    workflow = workflow_service.get_or_raise(workflow_run_id)
    data = {
        "workflow_run_id": workflow_run_id,
        "section_plan": getattr(workflow, "section_plan", []),
        "section_progress": getattr(
            workflow,
            "section_progress",
            {"total": 0, "completed": 0, "running": 0, "failed": 0, "pending": 0},
        ),
    }
    logger.info(
        "workflows.sections.completed workflow_run_id=%s total=%s completed=%s failed=%s",
        workflow_run_id,
        data["section_progress"].get("total", 0),
        data["section_progress"].get("completed", 0),
        data["section_progress"].get("failed", 0),
    )
    return success_response(data)


@router.get("/{workflow_run_id}/observability")
async def get_workflow_observability(
    workflow_run_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> object:
    logger.info("workflows.observability.started workflow_run_id=%s", workflow_run_id)
    workflow = workflow_service.get_or_raise(workflow_run_id)
    summary = getattr(workflow, "observability_summary", {}) or {}
    data = {"workflow_run_id": workflow_run_id, **summary}
    if verbose_logs_enabled():
        logger.info(
            "workflows.observability.completed workflow_run_id=%s keys=%s",
            workflow_run_id,
            sorted(summary.keys()),
        )
    return success_response(data)


@router.get("/{workflow_run_id}/errors")
async def get_workflow_errors(
    workflow_run_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> object:
    logger.info("workflows.errors.started workflow_run_id=%s", workflow_run_id)
    workflow = workflow_service.get_or_raise(workflow_run_id)
    errors = getattr(workflow, "errors", [])
    warnings = getattr(workflow, "warnings", [])
    logger.info(
        "workflows.errors.completed workflow_run_id=%s errors=%s warnings=%s",
        workflow_run_id,
        len(errors),
        len(warnings),
    )
    return success_response(
        {
            "errors": errors,
            "warnings": warnings,
        },
    )


@router.get("/{workflow_run_id}/diagnostics")
async def get_workflow_diagnostics(
    workflow_run_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> object:
    logger.info("workflows.diagnostics.started workflow_run_id=%s", workflow_run_id)
    workflow = workflow_service.get_or_raise(workflow_run_id)
    data = {
        "workflow_run_id": workflow_run_id,
        "status": workflow.status,
        "phases": getattr(workflow, "phases", []),
        "section_progress": getattr(
            workflow,
            "section_progress",
            {"total": 0, "completed": 0, "running": 0, "failed": 0, "pending": 0},
        ),
        "observability_summary": getattr(workflow, "observability_summary", {}),
        "errors": getattr(workflow, "errors", []),
        "warnings": getattr(workflow, "warnings", []),
    }
    logger.info(
        "workflows.diagnostics.completed workflow_run_id=%s status=%s errors=%s warnings=%s",
        workflow_run_id,
        workflow.status,
        len(data["errors"]),
        len(data["warnings"]),
    )
    return success_response(data)
```

#### `backend/core/__init__.py`

**Language hint:** `python`

```python
"""Shared foundation for the AI SDLC backend."""
```

#### `backend/core/config.py`

**Language hint:** `python`

```python
"""Application settings (pydantic-settings)."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.constants import DOCUMENT_INTELLIGENCE_USD_PER_PAGE

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ai-sdlc-backend"
    app_env: str = "development"
    app_debug: bool = True
    log_level: str = "INFO"
    logs_verbose: bool = False
    storage_root: Path = Field(default=Path("storage"))

    api_prefix: str = "/api"

    # Comma-separated browser origins, or "*" for any origin (SSE + API on another host).
    # With "*", credentials are disabled (browser rules). Example: https://app.example.com,https://www.example.com
    cors_origins: str = "*"

    # Kroki must not share the API server port; default 8001.
    kroki_url: str = "http://localhost:8001"

    azure_openai_api_key: str = ""
    azure_openai_api_version: str = "2024-02-01"
    azure_openai_gpt5_deployment: str = "gpt-5"
    azure_openai_gpt5mini_deployment: str = "gpt-5-mini"
    azure_openai_embedding_deployment: str = "text-embedding-3-small"
    azure_openai_endpoint: str = ""

    azure_search_api_key: str = ""
    azure_search_index_name: str = "sdlc-chunks"
    azure_search_endpoint: str = ""
    retrieval_top_k: int = 5
    chunker_token_mode: str = "tiktoken"

    azure_document_intelligence_key: str = ""
    azure_document_intelligence_endpoint: str = ""

    # Cost model (USD) — Document Intelligence prebuilt-layout, per page (env: DOCUMENT_INTELLIGENCE_USD_PER_PAGE).
    document_intelligence_usd_per_page: float = Field(default=DOCUMENT_INTELLIGENCE_USD_PER_PAGE)

    @property
    def documents_path(self) -> Path:
        return self.storage_root / "documents"

    @property
    def templates_path(self) -> Path:
        return self.storage_root / "templates"

    @property
    def workflows_path(self) -> Path:
        return self.storage_root / "workflows"

    @property
    def outputs_path(self) -> Path:
        return self.storage_root / "outputs"

    @property
    def diagrams_path(self) -> Path:
        return self.storage_root / "diagrams"

    @property
    def logs_path(self) -> Path:
        return self.storage_root / "logs"

    def ensure_storage_dirs(self) -> None:
        for path in (
            self.documents_path,
            self.templates_path,
            self.workflows_path,
            self.outputs_path,
            self.diagrams_path,
            self.logs_path,
        ):
            path.mkdir(parents=True, exist_ok=True)

    def cors_origin_list(self) -> list[str]:
        raw = (self.cors_origins or "").strip()
        if not raw or raw == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]

    def cors_allow_credentials(self) -> bool:
        """Wildcard origin is incompatible with credentialed cross-origin requests."""
        return self.cors_origin_list() != ["*"]


settings = Settings()


def ensure_storage_dirs() -> None:
    settings.ensure_storage_dirs()
```

#### `backend/core/constants.py`

**Language hint:** `python`

```python
"""Shared enums and pricing tables."""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class WorkflowStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class WorkflowPhase(StrEnum):
    INPUT_PREPARATION = "INPUT_PREPARATION"
    INGESTION = "INGESTION"
    TEMPLATE_PREPARATION = "TEMPLATE_PREPARATION"
    SECTION_PLANNING = "SECTION_PLANNING"
    RETRIEVAL = "RETRIEVAL"
    GENERATION = "GENERATION"
    ASSEMBLY_VALIDATION = "ASSEMBLY_VALIDATION"
    RENDER_EXPORT = "RENDER_EXPORT"


class DocType(StrEnum):
    PDD = "PDD"
    SDD = "SDD"
    UAT = "UAT"


class OutputFormat(StrEnum):
    DOCX = "DOCX"
    XLSX = "XLSX"


class TemplateSource(StrEnum):
    INBUILT = "inbuilt"
    CUSTOM = "custom"


class TemplateStatus(StrEnum):
    PENDING = "PENDING"
    COMPILING = "COMPILING"
    READY = "READY"
    FAILED = "FAILED"


class DocumentStatus(StrEnum):
    UPLOADED = "UPLOADED"
    READY = "READY"
    FAILED = "FAILED"


class DocumentIngestionStatus(StrEnum):
    """BRD indexing lifecycle in Azure AI Search (once per document_id)."""

    NOT_STARTED = "NOT_STARTED"
    INDEXED = "INDEXED"
    FAILED = "FAILED"


# Same ID shape as custom uploads (`tpl-` prefix) but stable and discoverable in API lists.
INBUILT_TEMPLATE_ID_PDD: Final[str] = "tpl-inbuilt-pdd"
INBUILT_TEMPLATE_ID_SDD: Final[str] = "tpl-inbuilt-sdd"
INBUILT_TEMPLATE_ID_UAT: Final[str] = "tpl-inbuilt-uat"

INBUILT_TEMPLATE_ID_BY_DOC_TYPE: Final[dict[DocType, str]] = {
    DocType.PDD: INBUILT_TEMPLATE_ID_PDD,
    DocType.SDD: INBUILT_TEMPLATE_ID_SDD,
    DocType.UAT: INBUILT_TEMPLATE_ID_UAT,
}


def inbuilt_template_id_for(doc_type: str | DocType) -> str:
    """Resolve the canonical template_id for an inbuilt document type."""
    return INBUILT_TEMPLATE_ID_BY_DOC_TYPE[DocType(doc_type)]


PHASE_WEIGHTS: Final[dict[WorkflowPhase, float]] = {
    WorkflowPhase.INPUT_PREPARATION: 2.0,
    WorkflowPhase.INGESTION: 25.0,
    WorkflowPhase.TEMPLATE_PREPARATION: 8.0,
    WorkflowPhase.SECTION_PLANNING: 5.0,
    WorkflowPhase.RETRIEVAL: 15.0,
    WorkflowPhase.GENERATION: 35.0,
    WorkflowPhase.ASSEMBLY_VALIDATION: 5.0,
    WorkflowPhase.RENDER_EXPORT: 5.0,
}

# --- LLM pricing ($ per 1K tokens) — update when Azure pricing changes ---
# IMPORTANT: keys match TASK_TO_MODEL values / adapter aliases.
MODEL_PRICING: Final[dict[str, dict[str, float]]] = {
    "gpt-5": {"input": 0.015, "output": 0.060},
    "gpt-5-mini": {"input": 0.00015, "output": 0.0006},
    "text-embedding-3-large": {"input": 0.00013, "output": 0.0},
    "text-embedding-3-small": {"input": 0.00002, "output": 0.0},
}

# --- LLM task routing ---
TASK_TO_MODEL: Final[dict[str, str]] = {
    "diagram_generation": "gpt-5",
    "diagram_correction": "gpt-5",
    "complex_section": "gpt-5",
    "text_generation": "gpt-5-mini",
    "table_generation": "gpt-5-mini",
    "template_classification": "gpt-5-mini",
    "retrieval_query_generation": "gpt-5-mini",
}

# Keep lightweight tasks lean; reserve stronger reasoning for genuinely harder tasks.
TASK_TO_REASONING_EFFORT: Final[dict[str, str]] = {
    "diagram_generation": "medium",
    "diagram_correction": "low",
    "complex_section": "high",
    "text_generation": "low",
    "table_generation": "low",
    "template_classification": "low",
    "retrieval_query_generation": "low",
}

# Smaller, task-aware budgets reduce the chance of spending the whole completion budget
# in reasoning with no visible content.
TASK_TO_MAX_COMPLETION_TOKENS: Final[dict[str, int]] = {
    "diagram_generation": 10000,
    "diagram_correction": 12000,
    "complex_section": 10000,
    "text_generation": 8000,
    "table_generation": 8000,
    "template_classification": 2000,
    "retrieval_query_generation": 1000,
}

# Azure Document Intelligence — rough $ per page (prebuilt-layout); tune to your SKU/region.
DOCUMENT_INTELLIGENCE_USD_PER_PAGE: Final[float] = 0.01
retrieval_max_concurrent_sections: int = 3
```

#### `backend/core/exceptions.py`

**Language hint:** `python`

```python
"""Domain exceptions."""

from __future__ import annotations


class SDLCBaseException(Exception):
    def __init__(self, message: str, code: str = "SDLC_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class ValidationException(SDLCBaseException):
    def __init__(self, message: str, code: str = "VALIDATION_ERROR") -> None:
        super().__init__(message, code)


class NotFoundException(SDLCBaseException):
    def __init__(self, resource: str, resource_id: str, code: str = "NOT_FOUND") -> None:
        self.resource = resource
        self.resource_id = resource_id
        super().__init__(f"{resource} not found: {resource_id}", code)


class WorkflowException(SDLCBaseException):
    def __init__(self, message: str, code: str = "WORKFLOW_ERROR") -> None:
        super().__init__(message, code)


class IngestionException(SDLCBaseException):
    def __init__(self, message: str, code: str = "INGESTION_ERROR") -> None:
        super().__init__(message, code)


class TemplateException(SDLCBaseException):
    def __init__(self, message: str, code: str = "TEMPLATE_ERROR") -> None:
        super().__init__(message, code)


class GenerationException(SDLCBaseException):
    def __init__(self, message: str, code: str = "GENERATION_ERROR") -> None:
        super().__init__(message, code)


class ExportException(SDLCBaseException):
    def __init__(self, message: str, code: str = "EXPORT_ERROR") -> None:
        super().__init__(message, code)
```

#### `backend/core/hosting.py`

**Language hint:** `python`

```python
"""Production hosting helpers: storage health and in-process task recovery."""

from __future__ import annotations

from pathlib import Path

from core.config import Settings
from core.constants import WorkflowStatus
from core.ids import utc_now_iso
from core.logging import get_logger
from repositories.workflow_repo import WorkflowRepository

logger = get_logger(__name__)

_RESTART_MSG = (
    "Workflow interrupted: the server restarted or the worker process ended before completion. "
    "Start a new workflow run if you still need this output."
)


def verify_storage_writable(storage_root: Path) -> bool:
    """Return True if ``storage_root`` can create and delete a small probe file."""
    storage_root.mkdir(parents=True, exist_ok=True)
    probe = storage_root / ".storage_write_probe"
    try:
        probe.write_bytes(b"ok")
        return True
    except OSError as exc:
        logger.error(
            "storage_not_writable path=%s detail=%s",
            storage_root,
            exc,
        )
        return False
    finally:
        try:
            if probe.is_file():
                probe.unlink()
        except OSError:
            pass


def reconcile_interrupted_workflows(repo: WorkflowRepository) -> int:
    """
    Mark ``RUNNING`` workflows as ``FAILED`` after a process restart.

    Background work is dispatched with FastAPI BackgroundTasks; it does not survive
    restarts. This avoids workflows stuck in RUNNING forever.
    """
    n = 0
    for w in repo.list_all():
        if w.status != WorkflowStatus.RUNNING.value:
            continue
        err = {
            "code": "SERVER_RESTART",
            "detail": _RESTART_MSG,
            "at": utc_now_iso(),
        }
        errors = [*w.errors, err]
        repo.update(
            w.workflow_run_id,
            status=WorkflowStatus.FAILED.value,
            current_phase=w.current_phase,
            current_step_label=_RESTART_MSG,
            errors=errors,
        )
        n += 1
        logger.warning(
            "workflow_marked_failed_after_restart workflow_run_id=%s",
            w.workflow_run_id,
        )
    return n


def run_hosting_startup(settings: Settings) -> None:
    """Storage probe + orphaned workflow reconciliation (call from app lifespan)."""
    if not verify_storage_writable(settings.storage_root):
        logger.error(
            "Set STORAGE_ROOT to a persistent, writable directory (mounted volume in Azure "
            "Container Apps/App Service, Kubernetes PVC, etc.)."
        )
    reconcile_interrupted_workflows(WorkflowRepository(settings.workflows_path))
```

#### `backend/core/ids.py`

**Language hint:** `python`

```python
"""ID helpers and timestamps."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _hex12() -> str:
    return uuid.uuid4().hex[:12]


def workflow_id() -> str:
    return f"wf-{_hex12()}"


def document_id() -> str:
    return f"doc-{_hex12()}"


def template_id() -> str:
    return f"tpl-{_hex12()}"


def output_id() -> str:
    return f"out-{_hex12()}"


def section_id() -> str:
    return f"sec-{_hex12()}"


def chunk_id() -> str:
    return f"chk-{_hex12()}"


def call_id() -> str:
    return f"call-{_hex12()}"


def chunk_id_for_document(document_id: str, chunk_index: int) -> str:
    """Stable chunk key for Azure Search upserts (ingest-once, idempotent)."""
    return f"{document_id}_chunk_{chunk_index:06d}"
```

#### `backend/core/logging.py`

**Language hint:** `python`

```python
"""Logging helpers for local development and workflow files."""

from __future__ import annotations

import logging
from pathlib import Path

from core.config import settings


def configure_logging(level: int | None = None) -> None:
    resolved_level_name = (settings.log_level or "").upper()
    resolved_level = getattr(logging, resolved_level_name, logging.INFO)
    if level is not None:
        resolved_level = level
    logging.basicConfig(
        level=resolved_level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def verbose_logs_enabled() -> bool:
    return bool(settings.logs_verbose)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def get_workflow_log_path(workflow_run_id: str) -> Path:
    return settings.logs_path / f"{workflow_run_id}.log"


def get_workflow_observability_path(workflow_run_id: str) -> Path:
    return settings.logs_path / f"{workflow_run_id}_observability.jsonl"
```

#### `backend/core/response.py`

**Language hint:** `python`

```python
"""Standard API response envelope helpers."""

from __future__ import annotations

from fastapi.responses import JSONResponse


def success_response(
    data: object,
    message: str = "Success",
    meta: dict[str, object] | None = None,
    status_code: int = 200,
) -> JSONResponse:
    payload = {
        "success": True,
        "message": message,
        "data": data,
        "errors": [],
        "meta": meta or {},
    }
    return JSONResponse(content=payload, status_code=status_code)


def created_response(
    data: object,
    message: str = "Created",
    meta: dict[str, object] | None = None,
) -> JSONResponse:
    return success_response(data=data, message=message, meta=meta, status_code=201)


def error_response(
    message: str,
    errors: list[dict[str, object]] | None = None,
    status_code: int = 400,
    meta: dict[str, object] | None = None,
) -> JSONResponse:
    payload = {
        "success": False,
        "message": message,
        "data": None,
        "errors": errors or [],
        "meta": meta or {},
    }
    return JSONResponse(content=payload, status_code=status_code)
```

#### `backend/core/token_count.py`

**Language hint:** `python`

```python
"""Token counting helpers with tiktoken fallback behavior."""

from __future__ import annotations

import re
from functools import lru_cache

_FALLBACK_TOKEN_RE = re.compile(r"\S+")


@lru_cache(maxsize=1)
def _get_encoding():
    try:
        import tiktoken  # type: ignore

        return tiktoken.get_encoding("cl100k_base")
    except Exception:
        return None


def count_tokens(text: str) -> int:
    """Count tokens using tiktoken when available; fallback to whitespace tokens."""
    content = text or ""
    encoding = _get_encoding()
    if encoding is not None:
        try:
            return len(encoding.encode(content))
        except Exception:
            pass
    return len(_FALLBACK_TOKEN_RE.findall(content))
```

#### `backend/infrastructure/__init__.py`

**Language hint:** `python`

```python
"""Infrastructure adapters for external systems."""

from infrastructure.doc_intelligence import AzureDocIntelligenceClient
from infrastructure.search_client import AzureSearchClient
from infrastructure.sk_adapter import AzureSKAdapter

__all__ = [
    "AzureDocIntelligenceClient",
    "AzureSKAdapter",
    "AzureSearchClient",
]
```

#### `backend/infrastructure/doc_intelligence.py`

**Language hint:** `python`

```python
"""Azure Document Intelligence adapter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from core.config import settings
from core.exceptions import IngestionException
from core.logging import get_logger, verbose_logs_enabled

logger = get_logger(__name__)

DOC_INTELLIGENCE_API_VERSION = "2024-11-30"


@dataclass(slots=True)
class ParsedTable:
    markdown: str
    page_number: int | None
    row_count: int
    column_count: int


@dataclass(slots=True)
class ParsedDocument:
    full_text: str
    page_count: int
    language: str | None
    tables: list[ParsedTable]
    raw_result: dict[str, Any]


class AzureDocIntelligenceClient:
    """Thin adapter around Azure Document Intelligence REST API."""

    def __init__(
        self,
        *,
        endpoint: str | None = None,
        api_key: str | None = None,
        api_version: str = DOC_INTELLIGENCE_API_VERSION,
    ) -> None:
        self._endpoint = (endpoint or settings.azure_document_intelligence_endpoint).rstrip("/")
        self._api_key = api_key or settings.azure_document_intelligence_key
        self._api_version = api_version

    def is_configured(self) -> bool:
        return bool(self._endpoint and self._api_key)

    async def analyze_document(self, payload: bytes, *, content_type: str = "application/octet-stream") -> ParsedDocument:
        if not self.is_configured():
            raise IngestionException("Azure Document Intelligence is not configured.")

        analyze_url = (
            f"{self._endpoint}/documentintelligence/documentModels/prebuilt-layout:analyze"
            f"?api-version={self._api_version}"
        )
        headers = {
            "Ocp-Apim-Subscription-Key": self._api_key,
            "Content-Type": content_type,
        }
        if verbose_logs_enabled():
            logger.info(
                "doc_intelligence.submit endpoint=%s content_type=%s payload_bytes=%s api_version=%s",
                self._endpoint,
                content_type,
                len(payload),
                self._api_version,
            )

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                analyze_response = await client.post(analyze_url, headers=headers, content=payload)
                analyze_response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response_body = exc.response.text[:4000] if exc.response is not None else ""
                logger.exception(
                    "doc_intelligence.submit_http_error status_code=%s body=%s",
                    exc.response.status_code if exc.response is not None else "unknown",
                    response_body,
                )
                raise IngestionException(
                    f"Document Intelligence submit failed with status "
                    f"{exc.response.status_code if exc.response is not None else 'unknown'}: {response_body}"
                ) from exc
            except Exception as exc:
                logger.exception("docintelligence.submit.failed error=%s", str(exc))
                raise IngestionException(f"Document Intelligence submit failed: {exc}") from exc

            operation_location = analyze_response.headers.get("operation-location")
            if not operation_location:
                raise IngestionException("Document Intelligence response missing operation-location header.")
            if verbose_logs_enabled():
                logger.info("docintelligence.submit.completed operation_location=%s", operation_location)

            result = await self._poll_operation(client, operation_location, headers)
            return self._to_parsed_document(result)

    async def _poll_operation(
        self,
        client: httpx.AsyncClient,
        operation_location: str,
        headers: dict[str, str],
    ) -> dict[str, Any]:
        for attempt in range(60):
            try:
                response = await client.get(operation_location, headers=headers)
                response.raise_for_status()
                body = response.json()
            except httpx.HTTPStatusError as exc:
                response_body = exc.response.text[:4000] if exc.response is not None else ""
                logger.exception(
                    "doc_intelligence.poll_http_error attempt=%s status_code=%s body=%s",
                    attempt + 1,
                    exc.response.status_code if exc.response is not None else "unknown",
                    response_body,
                )
                raise IngestionException(
                    f"Document Intelligence polling failed with status "
                    f"{exc.response.status_code if exc.response is not None else 'unknown'}: {response_body}"
                ) from exc
            except Exception as exc:
                logger.exception("docintelligence.poll.failed attempt=%s error=%s", attempt + 1, str(exc))
                raise IngestionException(f"Document Intelligence polling failed: {exc}") from exc
            status = str(body.get("status", "")).lower()
            if verbose_logs_enabled():
                logger.info("docintelligence.poll.status attempt=%s status=%s", attempt + 1, status)
            if status == "succeeded":
                analyze_result = body.get("analyzeResult")
                if not isinstance(analyze_result, dict):
                    raise IngestionException("Document Intelligence returned invalid analyzeResult payload.")
                return analyze_result
            if status == "failed":
                raise IngestionException(f"Document Intelligence analysis failed: {body}")
        raise IngestionException("Timed out waiting for Document Intelligence analysis result.")

    def _to_parsed_document(self, result: dict[str, Any]) -> ParsedDocument:
        content = str(result.get("content") or "")
        pages = result.get("pages") or []
        page_count = len(pages) if isinstance(pages, list) else 0
        languages = result.get("languages") or []
        language = None
        if isinstance(languages, list) and languages:
            first = languages[0]
            if isinstance(first, dict):
                language = first.get("locale")
        tables: list[ParsedTable] = []
        for table in result.get("tables") or []:
            if not isinstance(table, dict):
                continue
            markdown = self._table_to_markdown(table)
            tables.append(
                ParsedTable(
                    markdown=markdown,
                    page_number=self._resolve_table_page(table),
                    row_count=int(table.get("rowCount") or 0),
                    column_count=int(table.get("columnCount") or 0),
                ),
            )
        logger.info(
            "docintelligence.analyze.completed page_count=%s table_count=%s language=%s text_len=%s",
            page_count,
            len(tables),
            language,
            len(content),
        )
        return ParsedDocument(
            full_text=content,
            page_count=page_count,
            language=language,
            tables=tables,
            raw_result=result,
        )

    def _resolve_table_page(self, table: dict[str, Any]) -> int | None:
        spans = table.get("boundingRegions") or []
        if not spans or not isinstance(spans, list):
            return None
        first = spans[0]
        if not isinstance(first, dict):
            return None
        page = first.get("pageNumber")
        return int(page) if isinstance(page, int | float) else None

    def _table_to_markdown(self, table: dict[str, Any]) -> str:
        rows = int(table.get("rowCount") or 0)
        cols = int(table.get("columnCount") or 0)
        if rows <= 0 or cols <= 0:
            return ""

        matrix = [["" for _ in range(cols)] for _ in range(rows)]
        for cell in table.get("cells") or []:
            if not isinstance(cell, dict):
                continue
            row_idx = int(cell.get("rowIndex") or 0)
            col_idx = int(cell.get("columnIndex") or 0)
            if 0 <= row_idx < rows and 0 <= col_idx < cols:
                matrix[row_idx][col_idx] = str(cell.get("content") or "").strip().replace("\n", " ")

        header = matrix[0]
        lines = [
            f"| {' | '.join(header)} |",
            f"| {' | '.join(['---'] * cols)} |",
        ]
        for row in matrix[1:]:
            lines.append(f"| {' | '.join(row)} |")
        return "\n".join(lines)
```

#### `backend/infrastructure/search_client.py`

**Language hint:** `python`

```python
"""Azure AI Search adapter."""
from __future__ import annotations

import asyncio
import json
import logging
import random
from dataclasses import dataclass
from typing import Any
from time import perf_counter

import httpx

from core.config import settings
from core.exceptions import IngestionException

logger = logging.getLogger(__name__)

SEARCH_API_VERSION = "2025-09-01"

# Phase 1 + Phase 3 configuration
SEARCH_RETRYABLE_STATUS_CODES = {429, 502, 503, 504}
SEARCH_MAX_RETRY_ATTEMPTS = 4
SEARCH_RETRY_BASE_DELAY_SECONDS = 1.0
SEARCH_RETRY_MAX_DELAY_SECONDS = 8.0
SEARCH_RETRY_JITTER_MAX_SECONDS = 0.25

SEARCH_DEFAULT_TIMEOUT_SECONDS = 45.0
SEARCH_INDEX_TIMEOUT_SECONDS = 60.0


@dataclass(slots=True)
class SearchChunk:
    chunk_id: str
    document_id: str
    workflow_run_id: str
    text: str
    chunk_index: int
    section_heading: str | None
    page_number: int | None
    content_type: str
    embedding: list[float]


class AzureSearchClient:
    """Adapter for indexing and hybrid retrieval operations."""

    def __init__(
        self,
        *,
        endpoint: str | None = None,
        api_key: str | None = None,
        index_name: str | None = None,
        api_version: str = SEARCH_API_VERSION,
    ) -> None:
        self._endpoint = (endpoint or settings.azure_search_endpoint).rstrip("/")
        self._api_key = api_key or settings.azure_search_api_key
        self._index_name = index_name or settings.azure_search_index_name
        self._api_version = api_version

        # Phase 3: reusable async HTTP client
        self._client: httpx.AsyncClient | None = None

    def is_configured(self) -> bool:
        return bool(self._endpoint and self._api_key and self._index_name)

    def _get_client(self, *, timeout_seconds: float) -> httpx.AsyncClient:
        """
        Lazily create and reuse a single AsyncClient.
        If an existing client has a different timeout requirement, keep the existing
        one to preserve connection reuse. The default timeout is already sufficient
        for search calls.
        """
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=timeout_seconds)
        return self._client

    async def aclose(self) -> None:
        """Close the reusable HTTP client if it exists."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @staticmethod
    def _safe_json(response: httpx.Response):
        try:
            return response.json()
        except Exception:
            return None

    @staticmethod
    def _summarize_index_payload(payload: dict) -> dict:
        docs = payload.get("value") or []
        dims = []
        samples = []

        for doc in docs:
            emb = doc.get("embedding")
            if isinstance(emb, list):
                dims.append(len(emb))

        for doc in docs[:2]:
            sample = {k: v for k, v in doc.items() if k != "embedding"}
            emb = doc.get("embedding")
            if isinstance(emb, list):
                sample["embedding_dim"] = len(emb)
                sample["embedding_head"] = emb[:3]
            else:
                sample["embedding_dim"] = None
            samples.append(sample)

        return {
            "document_count": len(docs),
            "embedding_dimensions_seen": sorted(set(dims)),
            "sample_documents": samples,
        }

    def _log_http_status_error(self, operation: str, payload: dict, exc: httpx.HTTPStatusError) -> None:
        response = exc.response
        request = exc.request
        details = {
            "operation": operation,
            "method": request.method if request else None,
            "url": str(request.url) if request else None,
            "status_code": response.status_code if response else None,
            "reason_phrase": response.reason_phrase if response else None,
            "x_ms_request_id": response.headers.get("x-ms-request-id") if response else None,
            "x_ms_client_request_id": response.headers.get("x-ms-client-request-id") if response else None,
            "index_name": getattr(self, "_index_name", None),
            "api_version": getattr(self, "_api_version", None),
            "response_json": self._safe_json(response) if response else None,
            "response_text": (response.text[:8000] if response and response.text else None),
            "request_payload_summary": self._summarize_index_payload(payload),
        }
        logger.error(
            "Azure Search HTTP error during %s:\n%s",
            operation,
            json.dumps(details, indent=2, ensure_ascii=False, default=str),
        )

    def _compute_retry_delay_seconds(
        self,
        attempt: int,
        response: httpx.Response | None = None,
    ) -> float:
        """
        Prefer Retry-After if present; otherwise exponential backoff + jitter.
        """
        if response is not None:
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                try:
                    retry_after_seconds = float(retry_after)
                    if retry_after_seconds > 0:
                        return min(retry_after_seconds, SEARCH_RETRY_MAX_DELAY_SECONDS)
                except ValueError:
                    pass

        base_delay = min(
            SEARCH_RETRY_MAX_DELAY_SECONDS,
            SEARCH_RETRY_BASE_DELAY_SECONDS * (2 ** max(0, attempt - 1)),
        )
        jitter = random.uniform(0.0, SEARCH_RETRY_JITTER_MAX_SECONDS)
        return min(base_delay + jitter, SEARCH_RETRY_MAX_DELAY_SECONDS)

    async def _post_json_with_retry(
        self,
        *,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any],
        operation: str,
        timeout_seconds: float,
    ) -> httpx.Response:
        """
        Retry transient Azure Search failures (especially 503 throttling / heavy load)
        and emit observability logs for retry behavior and latency.
        """
        client = self._get_client(timeout_seconds=timeout_seconds)
        last_request_error: httpx.RequestError | None = None
        started_at = perf_counter()

        for attempt in range(1, SEARCH_MAX_RETRY_ATTEMPTS + 1):
            attempt_started_at = perf_counter()

            try:
                response = await client.post(url, headers=headers, json=payload)
                attempt_duration_ms = int((perf_counter() - attempt_started_at) * 1000)

                if response.status_code in SEARCH_RETRYABLE_STATUS_CODES:
                    if attempt < SEARCH_MAX_RETRY_ATTEMPTS:
                        delay = self._compute_retry_delay_seconds(attempt, response)
                        logger.warning(
                            "search.retry.scheduled operation=%s attempt=%s/%s status_code=%s "
                            "delay_s=%.2f duration_ms=%s request_id=%s payload_summary=%s",
                            operation,
                            attempt,
                            SEARCH_MAX_RETRY_ATTEMPTS,
                            response.status_code,
                            delay,
                            attempt_duration_ms,
                            response.headers.get("x-ms-request-id"),
                            json.dumps(self._summarize_search_payload(payload), ensure_ascii=False, default=str),
                        )
                        await asyncio.sleep(delay)
                        continue

                response.raise_for_status()

                total_duration_ms = int((perf_counter() - started_at) * 1000)
                logger.info(
                    "search.request.succeeded operation=%s attempts=%s final_status=%s "
                    "duration_ms=%s request_id=%s payload_summary=%s",
                    operation,
                    attempt,
                    response.status_code,
                    total_duration_ms,
                    response.headers.get("x-ms-request-id"),
                    json.dumps(self._summarize_search_payload(payload), ensure_ascii=False, default=str),
                )
                return response

            except httpx.RequestError as exc:
                attempt_duration_ms = int((perf_counter() - attempt_started_at) * 1000)
                last_request_error = exc

                if attempt >= SEARCH_MAX_RETRY_ATTEMPTS:
                    total_duration_ms = int((perf_counter() - started_at) * 1000)
                    logger.exception(
                        "search.request.failed operation=%s attempts=%s error_type=request_error "
                        "duration_ms=%s payload_summary=%s error=%s",
                        operation,
                        attempt,
                        total_duration_ms,
                        json.dumps(self._summarize_search_payload(payload), ensure_ascii=False, default=str),
                        exc,
                    )
                    raise

                delay = self._compute_retry_delay_seconds(attempt, None)
                logger.warning(
                    "search.retry.scheduled operation=%s attempt=%s/%s error_type=request_error "
                    "delay_s=%.2f duration_ms=%s payload_summary=%s error=%s",
                    operation,
                    attempt,
                    SEARCH_MAX_RETRY_ATTEMPTS,
                    delay,
                    attempt_duration_ms,
                    json.dumps(self._summarize_search_payload(payload), ensure_ascii=False, default=str),
                    exc,
                )
                await asyncio.sleep(delay)

            except httpx.HTTPStatusError as exc:
                total_duration_ms = int((perf_counter() - started_at) * 1000)
                self._log_http_status_error(operation, payload, exc)
                logger.error(
                    "search.request.failed operation=%s attempts=%s error_type=http_status "
                    "status_code=%s duration_ms=%s request_id=%s payload_summary=%s",
                    operation,
                    attempt,
                    exc.response.status_code if exc.response is not None else "unknown",
                    total_duration_ms,
                    exc.response.headers.get("x-ms-request-id") if exc.response is not None else None,
                    json.dumps(self._summarize_search_payload(payload), ensure_ascii=False, default=str),
                )
                raise

        if last_request_error is not None:
            raise last_request_error

        raise RuntimeError(f"Unexpected Azure Search retry flow termination during {operation}")

    async def upsert_chunks(self, chunks: list[SearchChunk]) -> int:
        payload = {
            "value": [
                {
                    "@search.action": "mergeOrUpload",
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "workflow_run_id": chunk.workflow_run_id,
                    "text": chunk.text,
                    "chunk_index": chunk.chunk_index,
                    "section_heading": chunk.section_heading,
                    "page_number": chunk.page_number,
                    "content_type": chunk.content_type,
                    "embedding": chunk.embedding,
                }
                for chunk in chunks
            ]
        }
        url = (
            f"{self._endpoint}/indexes/{self._index_name}"
            f"/docs/index?api-version={self._api_version}"
        )
        headers = {
            "Content-Type": "application/json",
            "api-key": self._api_key,
        }

        logger.info(
            "Azure Search upsert summary: %s",
            json.dumps(self._summarize_index_payload(payload), ensure_ascii=False, default=str),
        )

        response = await self._post_json_with_retry(
            url=url,
            headers=headers,
            payload=payload,
            operation="upsert_chunks",
            timeout_seconds=SEARCH_INDEX_TIMEOUT_SECONDS,
        )

        body = self._safe_json(response) or {}
        results = body.get("value", [])
        failed = [item for item in results if not item.get("status", False)]
        if failed:
            logger.error(
                "Azure Search indexing reported per-document failures:\n%s",
                json.dumps(failed[:10], indent=2, ensure_ascii=False, default=str),
            )
            raise RuntimeError("Azure Search indexing completed with failed document statuses.")
        return len(results)

    async def hybrid_search(
        self,
        *,
        search_text: str,
        embedding: list[float],
        document_id: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        if not self.is_configured():
            raise IngestionException("Azure AI Search is not configured.")

        url = self._docs_search_url()
        payload = {
            "search": search_text,
            "filter": self.build_document_filter(document_id),
            "top": top_k,
            "vectorQueries": [
                {
                    "kind": "vector",
                    "vector": embedding,
                    "fields": "embedding",
                    "k": top_k,
                },
            ],
        }
        headers = {"Content-Type": "application/json", "api-key": self._api_key}

        logger.info(
            "search.request.started operation=hybrid_search index_name=%s payload_summary=%s",
            self._index_name,
            json.dumps(self._summarize_search_payload(payload), ensure_ascii=False, default=str),
        )

        response = await self._post_json_with_retry(
            url=url,
            headers=headers,
            payload=payload,
            operation="hybrid_search",
            timeout_seconds=SEARCH_DEFAULT_TIMEOUT_SECONDS,
        )

        body = response.json()
        value = body.get("value") or []
        return value if isinstance(value, list) else []

    async def delete_by_document(self, document_id: str) -> int:
        if not self.is_configured():
            raise IngestionException("Azure AI Search is not configured.")

        hits = await self._search_ids_for_document(document_id)
        ids = [str(item.get("chunk_id")) for item in hits if item.get("chunk_id")]
        if not ids:
            return 0

        actions = [{"@search.action": "delete", "chunk_id": chunk_id} for chunk_id in ids]
        payload = {"value": actions}
        headers = {"Content-Type": "application/json", "api-key": self._api_key}

        response = await self._post_json_with_retry(
            url=self._docs_index_url(),
            headers=headers,
            payload=payload,
            operation="delete_by_document",
            timeout_seconds=SEARCH_DEFAULT_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return len(ids)

    def build_document_filter(self, document_id: str) -> str:
        safe_document_id = document_id.replace("'", "''")
        return f"document_id eq '{safe_document_id}'"

    async def _search_ids_for_document(self, document_id: str) -> list[dict[str, Any]]:
        url = self._docs_search_url()
        payload = {
            "search": "*",
            "filter": self.build_document_filter(document_id),
            "top": 1000,
            "select": "chunk_id",
        }
        headers = {"Content-Type": "application/json", "api-key": self._api_key}

        response = await self._post_json_with_retry(
            url=url,
            headers=headers,
            payload=payload,
            operation="_search_ids_for_document",
            timeout_seconds=SEARCH_DEFAULT_TIMEOUT_SECONDS,
        )

        body = response.json()
        value = body.get("value") or []
        return value if isinstance(value, list) else []

    def _docs_index_url(self) -> str:
        return f"{self._endpoint}/indexes/{self._index_name}/docs/index?api-version={self._api_version}"

    def _docs_search_url(self) -> str:
        return f"{self._endpoint}/indexes/{self._index_name}/docs/search?api-version={self._api_version}"
   
    @staticmethod
    def _summarize_search_payload(payload: dict[str, Any]) -> dict[str, Any]:
        vector_queries = payload.get("vectorQueries") or []
        vector_dim = None
        if isinstance(vector_queries, list) and vector_queries:
            first = vector_queries[0]
            if isinstance(first, dict):
                vector = first.get("vector")
                if isinstance(vector, list):
                    vector_dim = len(vector)

        search_text = str(payload.get("search") or "")
        return {
            "search_text_length": len(search_text),
            "search_word_count": len(search_text.split()),
            "top": payload.get("top"),
            "has_filter": bool(payload.get("filter")),
            "vector_query_count": len(vector_queries) if isinstance(vector_queries, list) else 0,
            "vector_dimension": vector_dim,
        }
```

#### `backend/infrastructure/sk_adapter.py`

**Language hint:** `python`

```python
"""Azure OpenAI adapter (task-routed)."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Any

import httpx

from core.config import settings
from core.constants import (
    TASK_TO_MAX_COMPLETION_TOKENS,
    TASK_TO_MODEL,
    TASK_TO_REASONING_EFFORT,
)
from core.exceptions import GenerationException
from core.token_count import count_tokens

logger = logging.getLogger(__name__)

AZURE_OPENAI_TIMEOUT_SECONDS = 180.0
AZURE_OPENAI_CONNECT_TIMEOUT_SECONDS = 15.0
AZURE_OPENAI_WRITE_TIMEOUT_SECONDS = 30.0
AZURE_OPENAI_RETRIES = 2


@dataclass(frozen=True, slots=True)
class EmbeddingUsageResult:
    embedding: list[float]
    prompt_tokens: int


class AzureSKAdapter:
    """Task-routed LLM/embedding adapter for Azure OpenAI."""

    def __init__(
        self,
        *,
        endpoint: str | None = None,
        api_key: str | None = None,
        api_version: str | None = None,
        gpt5_deployment: str | None = None,
        gpt5mini_deployment: str | None = None,
        embedding_deployment: str | None = None,
    ) -> None:
        self._endpoint = (endpoint or settings.azure_openai_endpoint or "").rstrip("/")
        self._api_key = api_key or settings.azure_openai_api_key
        self._api_version = api_version or settings.azure_openai_api_version
        self._gpt5_deployment = gpt5_deployment or settings.azure_openai_gpt5_deployment
        self._gpt5mini_deployment = gpt5mini_deployment or settings.azure_openai_gpt5mini_deployment
        self._embedding_deployment = embedding_deployment or settings.azure_openai_embedding_deployment

    def is_configured(self) -> bool:
        return bool(self._endpoint and self._api_key)

    async def invoke_text(self, prompt: str, *, task: str = "default", cost_tracker=None) -> str:
        """
        Invoke a chat/completions model and return plain text.

        Behavior:
        - retries transport failures in _post_chat_completion()
        - retries empty assistant content once with a stricter prompt and lower reasoning effort
        - reduces completion budget on retry to avoid spending everything in reasoning
        """
        if not self.is_configured():
            raise GenerationException("Azure OpenAI is not configured.", code="MODEL_NOT_CONFIGURED")

        model_alias = self._resolve_model_for_task(task)

        body = await self._call_chat_completion(
            prompt=prompt,
            task=task,
            model_alias=model_alias,
        )
        text = self._extract_text_from_chat_response(body)

        if not text or not text.strip():
            logger.warning(
                "sk_adapter.empty_text_response task=%s model=%s raw_preview=%s",
                task,
                model_alias,
                str(body)[:2000].replace("\n", "\\n"),
            )

            finish_reason = self._extract_finish_reason(body)
            strict_prompt = self._make_strict_retry_prompt(prompt, task=task)

            retry_body = await self._call_chat_completion(
                prompt=strict_prompt,
                task=task,
                model_alias=model_alias,
                reasoning_effort_override="low",
                max_completion_tokens_override=self._retry_completion_budget(task),
            )
            retry_text = self._extract_text_from_chat_response(retry_body)

            if retry_text and retry_text.strip():
                body = retry_body
                text = retry_text
            else:
                logger.error(
                    "sk_adapter.empty_text_response_after_retry task=%s model=%s raw_preview=%s",
                    task,
                    model_alias,
                    str(retry_body)[:2000].replace("\n", "\\n"),
                )

                final_finish_reason = self._extract_finish_reason(retry_body) or finish_reason
                if final_finish_reason == "length":
                    raise GenerationException(
                        "Model exhausted completion budget without producing visible content.",
                        code="MODEL_RESPONSE_TRUNCATED",
                    )

                raise GenerationException(
                    "Model response is empty.",
                    code="INVALID_JSON_RESPONSE",
                )

        self._track_usage(
            cost_tracker,
            model_alias,
            task,
            body,
            prompt=prompt,
            output_text=text,
        )
        return text.strip()

    async def invoke_json(
        self,
        prompt: str,
        *,
        task: str,
        cost_tracker: Any | None = None,
    ) -> dict[str, Any]:
        """
        Invoke a chat model and parse the returned text as JSON object.
        """
        text = await self.invoke_text(prompt, task=task, cost_tracker=cost_tracker)

        logger.debug(
            "sk_adapter.invoke_json.raw_preview task=%s preview=%s",
            task,
            (text[:1200].replace("\n", "\\n") if isinstance(text, str) else str(text)[:1200]),
        )

        parsed = self._parse_json_payload(text)
        if not isinstance(parsed, dict):
            raise GenerationException(
                "Model returned non-object JSON payload.",
                code="JSON_OBJECT_REQUIRED",
            )

        return parsed

    async def generate_embedding(self, text: str) -> list[float]:
        result = await self.generate_embedding_with_usage(text)
        return result.embedding

    async def generate_embedding_with_usage(self, text: str) -> EmbeddingUsageResult:
        """
        Generate an embedding vector and return vector + prompt token usage.
        """
        if not self.is_configured():
            raise GenerationException("Azure OpenAI is not configured.", code="MODEL_NOT_CONFIGURED")

        if not self._embedding_deployment:
            raise GenerationException(
                "Embedding deployment is not configured.",
                code="EMBEDDING_MODEL_NOT_CONFIGURED",
            )

        url = (
            f"{self._endpoint}/openai/deployments/{self._embedding_deployment}/embeddings"
            f"?api-version={self._api_version}"
        )
        headers = {"api-key": self._api_key}
        payload = {"input": text}

        timeout = httpx.Timeout(
            timeout=AZURE_OPENAI_TIMEOUT_SECONDS,
            connect=AZURE_OPENAI_CONNECT_TIMEOUT_SECONDS,
            write=AZURE_OPENAI_WRITE_TIMEOUT_SECONDS,
            read=AZURE_OPENAI_TIMEOUT_SECONDS,
        )

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            body = response.json()

        data = body.get("data") or []
        if not data or not isinstance(data, list):
            raise GenerationException(
                "Embedding response missing data field.",
                code="EMBEDDING_RESPONSE_INVALID",
            )

        embedding = data[0].get("embedding")
        if not isinstance(embedding, list):
            raise GenerationException(
                "Embedding response missing vector.",
                code="EMBEDDING_VECTOR_MISSING",
            )

        vector = [float(v) for v in embedding]
        usage = body.get("usage") or {}
        prompt_tokens = int(usage.get("prompt_tokens") or 0)
        if prompt_tokens <= 0:
            prompt_tokens = count_tokens(text)

        return EmbeddingUsageResult(embedding=vector, prompt_tokens=prompt_tokens)

    async def _call_chat_completion(
        self,
        *,
        prompt: str,
        task: str,
        model_alias: str,
        reasoning_effort_override: str | None = None,
        max_completion_tokens_override: int | None = None,
    ) -> dict[str, Any]:
        deployment = self._deployment_for_model(model_alias)

        payload: dict[str, Any] = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        }

        max_completion_tokens = (
            max_completion_tokens_override
            if max_completion_tokens_override is not None
            else TASK_TO_MAX_COMPLETION_TOKENS.get(task)
        )
        if max_completion_tokens:
            payload["max_completion_tokens"] = max_completion_tokens

        reasoning_effort = reasoning_effort_override or TASK_TO_REASONING_EFFORT.get(task)
        if reasoning_effort:
            payload["reasoning_effort"] = reasoning_effort

        return await self._post_chat_completion(deployment, payload, task=task)

    async def _post_chat_completion(
        self,
        deployment: str,
        payload: dict[str, Any],
        *,
        task: str,
    ) -> dict[str, Any]:
        url = f"{self._endpoint}/openai/deployments/{deployment}/chat/completions?api-version={self._api_version}"
        headers = {"api-key": self._api_key}

        timeout = httpx.Timeout(
            timeout=AZURE_OPENAI_TIMEOUT_SECONDS,
            connect=AZURE_OPENAI_CONNECT_TIMEOUT_SECONDS,
            write=AZURE_OPENAI_WRITE_TIMEOUT_SECONDS,
            read=AZURE_OPENAI_TIMEOUT_SECONDS,
        )

        last_error: Exception | None = None

        for attempt in range(1, AZURE_OPENAI_RETRIES + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(url, headers=headers, json=payload)
                    response.raise_for_status()
                    return response.json()

            except httpx.ReadTimeout as exc:
                last_error = exc
                logger.warning(
                    "sk_adapter.chat_timeout task=%s deployment=%s attempt=%s",
                    task,
                    deployment,
                    attempt,
                )
                if attempt >= AZURE_OPENAI_RETRIES:
                    raise GenerationException(
                        f"Azure OpenAI request timed out for task {task}.",
                        code="MODEL_TIMEOUT",
                    ) from exc

            except httpx.RequestError as exc:
                last_error = exc
                logger.warning(
                    "sk_adapter.chat_request_error task=%s deployment=%s attempt=%s detail=%s",
                    task,
                    deployment,
                    attempt,
                    str(exc),
                )
                if attempt >= AZURE_OPENAI_RETRIES:
                    raise GenerationException(
                        f"Azure OpenAI request failed for task {task}: {exc}",
                        code="MODEL_REQUEST_ERROR",
                    ) from exc

            except httpx.HTTPStatusError as exc:
                body_preview = exc.response.text[:2000] if exc.response is not None else ""
                raise GenerationException(
                    f"Azure OpenAI returned status {exc.response.status_code if exc.response else 'unknown'} "
                    f"for task {task}: {body_preview}",
                    code="MODEL_HTTP_ERROR",
                ) from exc

        raise GenerationException(
            f"Azure OpenAI request failed for task {task}: {last_error}",
            code="MODEL_REQUEST_ERROR",
        )

    def _deployment_for_model(self, model_alias: str) -> str:
        """
        Resolve model alias or deployment-like value into an Azure deployment name.
        """
        normalized = self._normalize_model_alias(model_alias)

        if normalized == "gpt5":
            if not self._gpt5_deployment:
                raise GenerationException(
                    "GPT-5 deployment is not configured.",
                    code="MODEL_NOT_CONFIGURED",
                )
            return self._gpt5_deployment

        if normalized == "gpt5mini":
            if not self._gpt5mini_deployment:
                raise GenerationException(
                    "GPT-5-mini deployment is not configured.",
                    code="MODEL_NOT_CONFIGURED",
                )
            return self._gpt5mini_deployment

        # If TASK_TO_MODEL stores an actual deployment name, allow it.
        if isinstance(model_alias, str) and model_alias.strip():
            return model_alias.strip()

        raise GenerationException(
            f"Unsupported model alias: {model_alias}",
            code="UNSUPPORTED_MODEL_ALIAS",
        )

    def _resolve_model_for_task(self, task: str | None) -> str:
        """
        Resolve which model alias to use for a given task.
        Strategy:
        1. Use TASK_TO_MODEL if defined.
        2. Prefer gpt5mini.
        3. Fallback to gpt5.
        """
        normalized_task = (task or "").strip().lower()
        model_alias = TASK_TO_MODEL.get(normalized_task)
        if isinstance(model_alias, str) and model_alias.strip():
            return model_alias.strip()

        if self._gpt5mini_deployment:
            return "gpt-5-mini"
        if self._gpt5_deployment:
            return "gpt-5"

        raise GenerationException(
            "Azure OpenAI deployment is not configured.",
            code="MODEL_NOT_CONFIGURED",
        )

    def _normalize_model_alias(self, value: str | None) -> str:
        if not value:
            return ""
        return re.sub(r"[\s_\-]", "", value.strip().lower())

    def _extract_text_from_chat_response(self, body: dict) -> str:
        """
        Extract assistant text from a chat completion response body.

        Supports:
        - choices[0].message.content as plain string
        - choices[0].message.content as structured list of parts
        - fallback to choices[0].text
        """
        if not isinstance(body, dict):
            return ""

        choices = body.get("choices") or []
        if not choices:
            return ""

        first = choices[0] or {}

        message = first.get("message") or {}
        content = message.get("content")

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict):
                    if isinstance(item.get("text"), str):
                        parts.append(item["text"])
                    elif item.get("type") == "text" and isinstance(item.get("content"), str):
                        parts.append(item["content"])
                elif isinstance(item, str):
                    parts.append(item)
            return "".join(parts).strip()

        text = first.get("text")
        if isinstance(text, str):
            return text

        return ""

    def _extract_finish_reason(self, body: dict[str, Any]) -> str | None:
        if not isinstance(body, dict):
            return None
        choices = body.get("choices") or []
        if not choices:
            return None
        first = choices[0] or {}
        reason = first.get("finish_reason")
        return str(reason) if isinstance(reason, str) else None

    def _extract_text(self, body: dict[str, Any]) -> str:
        """
        Backward-compatible alias for any older callers.
        """
        text = self._extract_text_from_chat_response(body)
        if text:
            return text

        raise GenerationException(
            "Completion response missing text content.",
            code="COMPLETION_TEXT_MISSING",
        )

    def _parse_json_payload(self, text: str) -> dict[str, Any]:
        """
        Parse model output into a JSON object.

        Tolerates:
        - fenced code blocks
        - leading/trailing explanatory text
        - smart quotes
        - trailing commas before } or ]
        """
        raw = (text or "").strip()
        if not raw:
            raise GenerationException("Model response is empty.", code="INVALID_JSON_RESPONSE")

        cleaned = self._coerce_json_candidate(raw)

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning(
                "sk_adapter.json_parse_failed preview=%s",
                raw[:1200].replace("\n", "\\n"),
            )
            raise GenerationException(
                "Model response is not valid JSON.",
                code="INVALID_JSON_RESPONSE",
            ) from None

        if not isinstance(parsed, dict):
            raise GenerationException(
                "Model response JSON must be an object.",
                code="INVALID_JSON_RESPONSE",
            )

        return parsed

    def _coerce_json_candidate(self, text: str) -> str:
        """
        Convert noisy model output into the most likely JSON candidate.
        """
        candidate = text.strip().lstrip("\ufeff")

        candidate = (
            candidate.replace("“", '"')
            .replace("”", '"')
            .replace("‘", "'")
            .replace("’", "'")
        )

        fenced = re.search(
            r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```",
            candidate,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if fenced:
            candidate = fenced.group(1).strip()
        else:
            extracted = self._extract_first_json_block(candidate)
            if extracted:
                candidate = extracted

        candidate = re.sub(r",\s*([}\]])", r"\1", candidate)
        return candidate

    def _extract_first_json_block(self, text: str) -> str | None:
        """
        Find the first balanced JSON object or array in free-form text.
        """
        starts = []
        obj_start = text.find("{")
        arr_start = text.find("[")

        if obj_start != -1:
            starts.append((obj_start, "{", "}"))
        if arr_start != -1:
            starts.append((arr_start, "[", "]"))

        if not starts:
            return None

        start_index, open_ch, close_ch = min(starts, key=lambda x: x[0])

        depth = 0
        in_string = False
        escape = False

        for idx in range(start_index, len(text)):
            ch = text[idx]

            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
                continue

            if ch == '"':
                in_string = True
                continue

            if ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
                if depth == 0:
                    return text[start_index : idx + 1]

        return None

    def _track_usage(
        self,
        cost_tracker: Any,
        model_alias: str,
        task: str,
        response_body: dict[str, Any] | None,
        *,
        prompt: str,
        output_text: str,
    ) -> None:
        """
        Best-effort usage tracking.

        Safe no-op if:
        - cost_tracker is None
        - usage block is missing
        - tracker shape is unsupported
        """
        if cost_tracker is None:
            return

        try:
            usage = response_body.get("usage", {}) if isinstance(response_body, dict) else {}
            prompt_tokens = int(usage.get("prompt_tokens") or 0)
            completion_tokens = int(usage.get("completion_tokens") or 0)
            total_tokens = int(usage.get("total_tokens") or (prompt_tokens + completion_tokens))

            if prompt_tokens <= 0:
                prompt_tokens = count_tokens(prompt or "")
            if completion_tokens <= 0:
                completion_tokens = count_tokens(output_text or "")
            if total_tokens <= 0:
                total_tokens = prompt_tokens + completion_tokens

            event = {
                "task": task,
                "model": model_alias,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "input_chars": len(prompt or ""),
                "output_chars": len(output_text or ""),
            }

            # Current generation tracker path
            track_call = getattr(cost_tracker, "track_call", None)
            if callable(track_call):
                track_call(
                    model=model_alias,
                    task=task,
                    input_tokens=prompt_tokens,
                    output_tokens=completion_tokens,
                )
                return

            # Dict/list compatibility
            if isinstance(cost_tracker, dict):
                cost_tracker.setdefault("calls", []).append(event)
                cost_tracker["call_count"] = int(cost_tracker.get("call_count", 0)) + 1
                cost_tracker["prompt_tokens"] = int(cost_tracker.get("prompt_tokens", 0)) + prompt_tokens
                cost_tracker["completion_tokens"] = int(cost_tracker.get("completion_tokens", 0)) + completion_tokens
                cost_tracker["total_tokens"] = int(cost_tracker.get("total_tokens", 0)) + total_tokens
                return

            if isinstance(cost_tracker, list):
                cost_tracker.append(event)
                return

            add_usage = getattr(cost_tracker, "add_usage", None)
            if callable(add_usage):
                add_usage(
                    task=task,
                    model=model_alias,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    prompt=prompt,
                    output_text=output_text,
                )
                return

        except Exception:
            logger.exception("sk_adapter.track_usage.failed task=%s model=%s", task, model_alias)

    def _make_strict_retry_prompt(self, prompt: str, *, task: str) -> str:
        if task == "template_classification":
            suffix = (
                "\n\nIMPORTANT:\n"
                "- Return ONLY a valid JSON object.\n"
                "- The JSON MUST contain a top-level key named \"sections\".\n"
                "- Do not include markdown fences.\n"
                "- Do not include commentary or explanations.\n"
            )
        elif "diagram" in task:
            suffix = (
                "\n\nIMPORTANT:\n"
                "- Return ONLY raw diagram syntax.\n"
                "- Do not include markdown fences.\n"
                "- Do not include explanation text.\n"
                "- If PlantUML is requested, include @startuml and @enduml.\n"
            )
        else:
            suffix = (
                "\n\nIMPORTANT:\n"
                "- Return ONLY the final answer content.\n"
                "- Do not include explanations before or after the answer.\n"
            )

        return f"{prompt.rstrip()}\n{suffix}"

    def _retry_completion_budget(self, task: str) -> int | None:
        original = TASK_TO_MAX_COMPLETION_TOKENS.get(task)
        if not original:
            return None

        # Retry with a smaller budget to discourage long internal reasoning chains.
        reduced = max(400, int(original * 0.6))
        return reduced
```

#### `backend/main.py`

**Language hint:** `python`

```python
"""FastAPI application entrypoint for the backend."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.router import api_router
from core.config import ensure_storage_dirs, settings
from core.exceptions import NotFoundException, SDLCBaseException
from core.hosting import run_hosting_startup
from core.logging import configure_logging
from core.response import error_response


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    ensure_storage_dirs()
    run_hosting_startup(settings)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=settings.app_debug, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list(),
        allow_credentials=settings.cors_allow_credentials(),
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(NotFoundException)
    async def handle_not_found(_: Request, exc: NotFoundException) -> JSONResponse:
        return error_response(
            message=exc.message,
            errors=[{"code": exc.code, "detail": exc.message}],
            status_code=404,
        )

    @app.exception_handler(SDLCBaseException)
    async def handle_sdlc_error(_: Request, exc: SDLCBaseException) -> JSONResponse:
        return error_response(
            message=exc.message,
            errors=[{"code": exc.code, "detail": exc.message}],
            status_code=400,
        )

    @app.exception_handler(Exception)
    async def handle_internal_error(_: Request, exc: Exception) -> JSONResponse:
        return error_response(
            message="Internal server error",
            errors=[{"code": "INTERNAL_ERROR", "detail": str(exc)}],
            status_code=500,
        )

    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
```

#### `backend/modules/__init__.py`

**Language hint:** `python`

```python
"""Domain modules."""
```

#### `backend/modules/assembly/__init__.py`

**Language hint:** `python`

```python
"""Assembly: ordered document structure before export."""

from __future__ import annotations

from modules.assembly.assembler import AssemblyOutcome, DocumentAssembler
from modules.assembly.models import AssembledDocument, AssembledSection

__all__ = ["AssembledDocument", "AssembledSection", "AssemblyOutcome", "DocumentAssembler"]
```

#### `backend/modules/assembly/assembler.py`

**Language hint:** `python`

```python
"""Merge section plan + generation results into a single ordered document."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from core.ids import utc_now_iso
from modules.assembly.models import AssembledDocument, AssembledSection
from modules.assembly.normalizer import normalize_section_content
from modules.generation.models import GenerationSectionResult
from modules.template.models import SectionDefinition


@dataclass(frozen=True, slots=True)
class AssemblyOutcome:
    document: AssembledDocument
    warnings: list[dict[str, object]] = field(default_factory=list)


class DocumentAssembler:
    def assemble(
        self,
        *,
        document_filename: str,
        doc_type: str,
        section_plan: list[SectionDefinition],
        section_generation_results: dict[str, dict[str, object]],
        export_mode: str = "final",
    ) -> AssemblyOutcome:
        ordered = sorted(section_plan, key=lambda s: s.execution_order)
        stem = Path(document_filename).stem
        title = f"{stem} — {doc_type}"

        sections: list[AssembledSection] = []
        warnings: list[dict[str, object]] = []
        ts = utc_now_iso()

        for idx, section in enumerate(ordered):
            raw = section_generation_results.get(section.section_id)
            if not raw:
                warnings.append(
                    {
                        "phase": "ASSEMBLY_VALIDATION",
                        "code": "missing_generation",
                        "section_id": section.section_id,
                        "title": section.title,
                        "message": f"No generation result for section {section.title!r}; section omitted from export.",
                        "at": ts,
                    },
                )
                continue

            row = GenerationSectionResult.model_validate(raw)

            child_titles = self._collect_immediate_or_nested_child_titles(
                ordered_sections=ordered,
                current_index=idx,
            )

            normalized = normalize_section_content(
                section_title=section.title,
                content=row.content or "",
                child_titles=child_titles,
                export_mode=export_mode,
            )

            if normalized.notes:
                warnings.append(
                    {
                        "phase": "ASSEMBLY_NORMALIZATION",
                        "code": "content_normalized",
                        "section_id": section.section_id,
                        "title": section.title,
                        "message": f"Normalized content for section {section.title!r}.",
                        "notes": normalized.notes,
                        "at": ts,
                    },
                )

            if row.output_type == "diagram" and not row.diagram_path:
                warnings.append(
                    {
                        "phase": "ASSEMBLY_VALIDATION",
                        "code": "diagram_path_missing",
                        "section_id": section.section_id,
                        "title": section.title,
                        "message": (
                            f"Diagram section {section.title!r} has no diagram_path; "
                            "the final export may show a heading without an image."
                        ),
                        "at": ts,
                    },
                )

            sections.append(
                AssembledSection(
                    section_id=section.section_id,
                    title=section.title,
                    level=int(section.level),
                    output_type=row.output_type,
                    content=normalized.content,
                    diagram_path=row.diagram_path,
                    content_blocks=[],
                    export_mode=export_mode,
                ),
            )

        return AssemblyOutcome(
            document=AssembledDocument(
                title=title,
                doc_type=doc_type,
                sections=sections,
                export_mode=export_mode,
            ),
            warnings=warnings,
        )

    def _collect_immediate_or_nested_child_titles(
        self,
        *,
        ordered_sections: list[SectionDefinition],
        current_index: int,
    ) -> list[str]:
        """
        Collect titles of child sections nested under the current section until the hierarchy closes.

        Example:
        current = level 1
        include subsequent level 2/3/... sections until we hit another level 1 or less.
        """
        current = ordered_sections[current_index]
        current_level = int(current.level)

        child_titles: list[str] = []
        for next_section in ordered_sections[current_index + 1:]:
            next_level = int(next_section.level)
            if next_level <= current_level:
                break
            child_titles.append(next_section.title)

        return child_titles
```

#### `backend/modules/assembly/models.py`

**Language hint:** `python`

```python
"""In-memory assembled document structures (post-generation, pre-export)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AssembledSection(BaseModel):
    """One section ready for export (no citation payloads — UI-only elsewhere)."""

    model_config = ConfigDict(extra="ignore")

    section_id: str
    title: str
    level: int = 1
    output_type: str = "text"
    content: str = ""
    diagram_path: str | None = None

    # Forward-compatible container for future semantic blocks
    content_blocks: list[dict[str, Any]] = Field(default_factory=list)

    # Per-section export mode (kept for compatibility; document-level mode is primary)
    export_mode: str = "final"


class AssembledDocument(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str
    doc_type: str
    sections: list[AssembledSection] = Field(default_factory=list)

    # NEW: document-wide export mode
    export_mode: str = "final"
```

#### `backend/modules/assembly/normalizer.py`

**Language hint:** `python`

```python
"""Normalize generated section content before export."""
from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class NormalizationResult:
    content: str
    notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Heading normalization / matching
# ---------------------------------------------------------------------------
_HEADING_RE = re.compile(r"^(\\)?(#{1,6})\s+(.+?)\s*$")
_NUMBERING_RE = re.compile(
    r"^(?:[A-Za-z]\.|(?:\d+(?:\.\d+)*)[.)]?)\s+",
    flags=re.IGNORECASE,
)

_DECORATIVE_WRAPPER_PATTERNS = (
    re.compile(r"^\s*\*\*_(.+?)_\*\*\s*$"),
    re.compile(r"^\s*__\*(.+?)\*__\s*$"),
    re.compile(r"^\s*\*\*(.+?)\*\*\s*$"),
)


def _normalize_heading_text(value: str) -> str:
    text = unicodedata.normalize("NFKC", value or "").strip().lower()
    text = re.sub(r"\s+", " ", text)

    m = _HEADING_RE.match(text)
    if m:
        text = m.group(3).strip().lower()

    text = _NUMBERING_RE.sub("", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _is_heading_line(line: str) -> bool:
    return _HEADING_RE.match(line.strip()) is not None


def _matches_section_title(line: str, section_title: str) -> bool:
    if not line.strip() or not section_title.strip():
        return False
    return _normalize_heading_text(line) == _normalize_heading_text(section_title)


# ---------------------------------------------------------------------------
# Internal drafting block stripping
# ---------------------------------------------------------------------------
_INTERNAL_LINE_PREFIXES = (
    "traceability notes",
    "key traceability notes",
    "source ",
    "sources:",
    "source:",
)

_INTERNAL_PLACEHOLDER_PATTERNS = (
    re.compile(r"<<\s*SCREENSHOT_", flags=re.IGNORECASE),
    re.compile(r"\[\s*people\.ey\.com\s*\]", flags=re.IGNORECASE),
)


def _looks_internal_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False

    lowered = stripped.lower()
    for prefix in _INTERNAL_LINE_PREFIXES:
        if lowered.startswith(prefix):
            return True

    for pattern in _INTERNAL_PLACEHOLDER_PATTERNS:
        if pattern.search(stripped):
            return True

    return False


def _strip_internal_lines(
    lines: list[str],
    *,
    section_title: str,
    export_mode: str,
    notes: list[str],
) -> list[str]:
    if export_mode != "final":
        return lines

    keep: list[str] = []
    removed_any = False

    section_title_norm = _normalize_heading_text(section_title)
    preserve_assumption_like = any(
        token in section_title_norm
        for token in ("assumption", "risk", "approval", "reviewer", "dependency")
    )

    i = 0
    while i < len(lines):
        line = lines[i]

        if _looks_internal_line(line):
            removed_any = True
            i += 1

            while i < len(lines) and (
                not lines[i].strip()
                or _looks_internal_line(lines[i])
                or lines[i].strip().startswith("(")
            ):
                i += 1
            continue

        lowered = line.strip().lower()

        if not preserve_assumption_like and lowered in {
            "assumptions and scope notes",
            "constraints and known gaps",
            "recommended immediate mitigations",
            "assumptions and constraints",
            "risks and follow-up",
        }:
            removed_any = True
            i += 1
            while i < len(lines) and lines[i].strip():
                i += 1
            continue

        keep.append(line)
        i += 1

    if removed_any:
        notes.append("internal_drafting_lines_removed")
    return keep


# ---------------------------------------------------------------------------
# Parent/subsection duplication trimming
# ---------------------------------------------------------------------------
def _trim_at_first_child_heading(
    lines: list[str],
    *,
    child_titles: Iterable[str],
    notes: list[str],
) -> list[str]:
    normalized_child_titles = {
        _normalize_heading_text(title)
        for title in child_titles
        if title and str(title).strip()
    }
    if not normalized_child_titles:
        return lines

    for idx, line in enumerate(lines):
        if not line.strip():
            continue
        if _is_heading_line(line):
            norm = _normalize_heading_text(line)
            if norm in normalized_child_titles:
                notes.append("trimmed_from_first_child_heading")
                return lines[:idx]

    return lines


# ---------------------------------------------------------------------------
# Leading duplicate title stripping
# ---------------------------------------------------------------------------
def _strip_leading_duplicate_heading(
    lines: list[str],
    *,
    section_title: str,
    notes: list[str],
) -> list[str]:
    if not lines:
        return lines

    idx = 0
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    if idx >= len(lines):
        return lines

    first = lines[idx]
    if _matches_section_title(first, section_title):
        notes.append("leading_duplicate_heading_removed")
        del lines[idx]

        if idx < len(lines) and not lines[idx].strip():
            del lines[idx]

    return lines


# ---------------------------------------------------------------------------
# Additional paragraph-level cleanup
# ---------------------------------------------------------------------------
_META_PARENT_PARAGRAPH_RE = re.compile(
    r"^(this section|this document|the following section|the following)\b.*"
    r"\b(defines|describes|captures|records|outlines|summarizes|documents|provides)\b",
    flags=re.IGNORECASE,
)


def _normalize_paragraph_key(value: str) -> str:
    text = unicodedata.normalize("NFKC", value or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _split_paragraphs(text: str) -> list[str]:
    if not text.strip():
        return []
    return [part.strip() for part in re.split(r"\n\s*\n", text.strip()) if part.strip()]


def _dedupe_paragraphs(text: str, *, notes: list[str]) -> str:
    paragraphs = _split_paragraphs(text)
    seen: set[str] = set()
    kept: list[str] = []
    removed = False

    for para in paragraphs:
        key = _normalize_paragraph_key(para)
        if not key:
            continue
        if key in seen:
            removed = True
            continue
        seen.add(key)
        kept.append(para)

    if removed:
        notes.append("duplicate_paragraphs_removed")

    return "\n\n".join(kept).strip()


def _remove_generic_parent_leadin(
    text: str,
    *,
    has_children: bool,
    notes: list[str],
) -> str:
    if not has_children:
        return text.strip()

    paragraphs = _split_paragraphs(text)
    if not paragraphs:
        return ""

    cleaned: list[str] = []
    removed = False

    for idx, para in enumerate(paragraphs):
        if idx == 0 and _META_PARENT_PARAGRAPH_RE.match(para):
            removed = True
            continue
        cleaned.append(para)

    if removed:
        notes.append("generic_parent_meta_leadin_removed")

    return "\n\n".join(cleaned).strip()


def _strip_decorative_emphasis(text: str, *, notes: list[str]) -> str:
    cleaned_lines: list[str] = []
    changed = False

    for line in text.splitlines():
        stripped = line.strip()
        replaced = False
        for pattern in _DECORATIVE_WRAPPER_PATTERNS:
            match = pattern.match(stripped)
            if match:
                cleaned_lines.append(match.group(1).strip())
                changed = True
                replaced = True
                break
        if not replaced:
            cleaned_lines.append(line)

    if changed:
        notes.append("decorative_markdown_emphasis_removed")

    return "\n".join(cleaned_lines).strip()


def _compress_parent_lists(
    text: str,
    *,
    has_children: bool,
    notes: list[str],
) -> str:
    if not has_children:
        return text.strip()

    lines = text.splitlines()
    bullet_re = re.compile(r"^\s*[-*•]\s+.+$")
    bullet_indices = [idx for idx, line in enumerate(lines) if bullet_re.match(line.strip())]

    if len(bullet_indices) <= 6:
        return text.strip()

    keep_indices = set(bullet_indices[:6])
    trimmed_lines: list[str] = []
    removed = False
    for idx, line in enumerate(lines):
        if idx in bullet_indices and idx not in keep_indices:
            removed = True
            continue
        trimmed_lines.append(line)

    if removed:
        notes.append("parent_bullet_list_trimmed")

    return "\n".join(trimmed_lines).strip()


# ---------------------------------------------------------------------------
# Public normalization entry point
# ---------------------------------------------------------------------------
def normalize_section_content(
    *,
    section_title: str,
    content: str,
    child_titles: Iterable[str] = (),
    export_mode: str = "final",
) -> NormalizationResult:
    """
    Normalize generated content before export.

    Current behaviors:
    - remove duplicated leading section title headings
    - remove internal drafting lines in final mode
    - trim parent-section content at first detected child heading
    - remove generic meta-summary lead-ins for parent sections
    - remove repeated paragraphs
    - remove decorative markdown emphasis wrappers
    - compress overly long parent bullet lists
    - collapse excessive blank lines
    """
    if not content:
        return NormalizationResult(content="", notes=[])

    notes: list[str] = []
    lines = content.splitlines()

    lines = _strip_leading_duplicate_heading(
        lines,
        section_title=section_title,
        notes=notes,
    )

    lines = _strip_internal_lines(
        lines,
        section_title=section_title,
        export_mode=export_mode,
        notes=notes,
    )

    lines = _trim_at_first_child_heading(
        lines,
        child_titles=child_titles,
        notes=notes,
    )

    text = "\n".join(lines).strip()
    text = _strip_decorative_emphasis(text, notes=notes)
    text = _remove_generic_parent_leadin(
        text,
        has_children=any(str(title).strip() for title in child_titles),
        notes=notes,
    )
    text = _compress_parent_lists(
        text,
        has_children=any(str(title).strip() for title in child_titles),
        notes=notes,
    )
    text = _dedupe_paragraphs(text, notes=notes)

    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return NormalizationResult(content=text, notes=notes)
```

#### `backend/modules/export/__init__.py`

**Language hint:** `python`

```python
"""Export: DOCX/XLSX renderers."""

from __future__ import annotations

from modules.export.renderer import ExportRenderer

__all__ = ["ExportRenderer"]
```

#### `backend/modules/export/content_blocks.py`

**Language hint:** `python`

```python
"""Semantic parsing helpers for generated markdown-ish / HTML-ish content."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from html import unescape
from typing import Literal

BlockKind = Literal[
    "heading",
    "paragraph",
    "bullet_list",
    "numbered_list",
    "table_gfm",
    "table_html",
    "image",
    "caption",
]


@dataclass(frozen=True, slots=True)
class ContentBlock:
    kind: BlockKind
    text: str = ""
    level: int = 0
    items: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    image_target: str | None = None
    image_alt: str | None = None


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------
_HEADING_RE = re.compile(r"^(\\)?(#{1,6})\s+(.+?)\s*$")
_BULLET_RE = re.compile(r"^\s*[-*•]\s+(.+?)\s*$")
_NUMBERED_RE = re.compile(r"^\s*\d+[.)]\s+(.+?)\s*$")

_MD_IMAGE_INLINE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
_MD_IMAGE_REF_RE = re.compile(r"!\[\]\[([^\]]+)\]")
_REF_STYLE_IMAGE_ID_RE = re.compile(r"image_[A-Za-z0-9+/=_\-]+")

_HTML_TABLE_START_RE = re.compile(r"<table\b", flags=re.IGNORECASE)
_HTML_TABLE_END_RE = re.compile(r"</table>", flags=re.IGNORECASE)
_HTML_ROW_RE = re.compile(r"<tr\b[^>]*>(.*?)</tr>", flags=re.IGNORECASE | re.DOTALL)
_HTML_CELL_RE = re.compile(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", flags=re.IGNORECASE | re.DOTALL)
_HTML_TAG_RE = re.compile(r"<[^>]+>")

_IMAGE_PATH_RE = re.compile(
    r"^[^\s]+\.(png|jpg|jpeg|gif|bmp|svg|webp)$",
    flags=re.IGNORECASE,
)

_SEPARATOR_CELL_RE = re.compile(r"^\s*:?-{3,}:?\s*$")

_INTERNAL_CAPTION_PREFIXES = (
    "figure ",
    "diagram ",
    "workflow diagram",
    "architecture diagram",
)


def _strip_html_tags(value: str) -> str:
    cleaned = _HTML_TAG_RE.sub("", value or "")
    cleaned = unescape(cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _unwrap_decorative_line(line: str) -> str:
    """
    Remove wrappers such as **_| a | b |_** or **text** when they surround a full line.
    """
    stripped = line.strip()
    wrappers = [
        ("**_", "_**"),
        ("**", "**"),
        ("__", "__"),
        ("_", "_"),
    ]
    for prefix, suffix in wrappers:
        if stripped.startswith(prefix) and stripped.endswith(suffix) and len(stripped) > len(prefix) + len(suffix):
            return stripped[len(prefix):-len(suffix)].strip()
    return stripped


def _is_table_line(line: str) -> bool:
    s = _unwrap_decorative_line(line).strip()
    return s.startswith("|") and s.endswith("|") and s.count("|") >= 2


def _split_pipe_row(line: str) -> list[str]:
    s = _unwrap_decorative_line(line).strip().strip("|")
    return [cell.strip() for cell in s.split("|")]


def _is_separator_row(line: str) -> bool:
    parts = _split_pipe_row(line)
    if not parts:
        return False
    return all(_SEPARATOR_CELL_RE.match(part) is not None for part in parts)


# ---------------------------------------------------------------------------
# Public helpers reused by existing code
# ---------------------------------------------------------------------------
def parse_gfm_table(block: str) -> list[list[str]]:
    """
    Parse a GitHub-flavored markdown pipe table into rows/cells.
    """
    raw_lines = [_unwrap_decorative_line(ln.rstrip()) for ln in block.strip().splitlines() if ln.strip()]
    table_lines = [ln for ln in raw_lines if _is_table_line(ln)]
    if not table_lines:
        return []

    rows: list[list[str]] = []
    for idx, line in enumerate(table_lines):
        if idx == 1 and _is_separator_row(line):
            continue
        rows.append(_split_pipe_row(line))
    return rows


def parse_html_table(block: str) -> list[list[str]]:
    """
    Parse a simple HTML table into rows/cells.
    Supports <table><tr><td>/<th> structures commonly leaked by generators.
    """
    rows: list[list[str]] = []
    for row_match in _HTML_ROW_RE.finditer(block):
        row_html = row_match.group(1)
        cells = [_strip_html_tags(cell_html) for cell_html in _HTML_CELL_RE.findall(row_html)]
        if cells:
            rows.append(cells)
    return rows


# ---------------------------------------------------------------------------
# Semantic block parser
# ---------------------------------------------------------------------------
def parse_content_blocks(content: str) -> list[ContentBlock]:
    """
    Parse mixed markdown-ish / HTML-ish generated content into semantic blocks.

    Supports:
    - ATX headings: ## Heading
    - escaped headings: \\## Heading
    - bullet lists
    - numbered lists
    - GFM tables
    - HTML tables
    - markdown images
    - reference-style image tokens like ![][image_xxx]
    - normal paragraphs
    """
    if not content or not content.strip():
        return []

    lines = content.splitlines()
    blocks: list[ContentBlock] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = _unwrap_decorative_line(line).strip()

        if not stripped:
            i += 1
            continue

        # ------------------------------------------------------------------
        # HTML table block
        # ------------------------------------------------------------------
        if _HTML_TABLE_START_RE.search(stripped):
            start = i
            i += 1
            while i < len(lines) and not _HTML_TABLE_END_RE.search(lines[i]):
                i += 1
            if i < len(lines):
                i += 1  # include closing </table>
            block = "\n".join(lines[start:i])
            rows = parse_html_table(block)
            if rows:
                blocks.append(ContentBlock(kind="table_html", rows=rows, text=block))
            continue

        # ------------------------------------------------------------------
        # GFM table block
        # ------------------------------------------------------------------
        if _is_table_line(stripped):
            start = i
            while i < len(lines) and _is_table_line(lines[i]):
                i += 1
            block = "\n".join(lines[start:i])
            rows = parse_gfm_table(block)
            if rows:
                blocks.append(ContentBlock(kind="table_gfm", rows=rows, text=block))
            continue

        # ------------------------------------------------------------------
        # Heading block
        # ------------------------------------------------------------------
        heading_match = _HEADING_RE.match(stripped)
        if heading_match:
            hashes = heading_match.group(2)
            text = heading_match.group(3).strip()
            blocks.append(
                ContentBlock(
                    kind="heading",
                    text=text,
                    level=len(hashes),
                )
            )
            i += 1
            continue

        # ------------------------------------------------------------------
        # Markdown image block
        # ------------------------------------------------------------------
        inline_img = _MD_IMAGE_INLINE_RE.search(stripped)
        if inline_img:
            alt = inline_img.group(1).strip()
            target = inline_img.group(2).strip()
            blocks.append(
                ContentBlock(
                    kind="image",
                    text=stripped,
                    image_target=target,
                    image_alt=alt or None,
                )
            )
            i += 1

            if i < len(lines):
                nxt = _unwrap_decorative_line(lines[i]).strip()
                if nxt and nxt.lower().startswith(_INTERNAL_CAPTION_PREFIXES):
                    blocks.append(ContentBlock(kind="caption", text=nxt))
                    i += 1
            continue

        ref_img = _MD_IMAGE_REF_RE.search(stripped)
        if ref_img or _REF_STYLE_IMAGE_ID_RE.search(stripped):
            image_id = ref_img.group(1).strip() if ref_img else stripped
            blocks.append(
                ContentBlock(
                    kind="image",
                    text=stripped,
                    image_target=image_id,
                    image_alt=None,
                )
            )
            i += 1

            if i < len(lines):
                nxt = _unwrap_decorative_line(lines[i]).strip()
                if nxt and nxt.lower().startswith(_INTERNAL_CAPTION_PREFIXES):
                    blocks.append(ContentBlock(kind="caption", text=nxt))
                    i += 1
            continue

        # ------------------------------------------------------------------
        # Bare image path block
        # ------------------------------------------------------------------
        if _IMAGE_PATH_RE.match(stripped):
            blocks.append(
                ContentBlock(
                    kind="image",
                    text=stripped,
                    image_target=stripped,
                    image_alt=None,
                )
            )
            i += 1

            if i < len(lines):
                nxt = _unwrap_decorative_line(lines[i]).strip()
                if nxt and nxt.lower().startswith(_INTERNAL_CAPTION_PREFIXES):
                    blocks.append(ContentBlock(kind="caption", text=nxt))
                    i += 1
            continue

        # ------------------------------------------------------------------
        # Bullet list block
        # ------------------------------------------------------------------
        bullet_match = _BULLET_RE.match(stripped)
        if bullet_match:
            items: list[str] = []
            while i < len(lines):
                candidate = _unwrap_decorative_line(lines[i]).strip()
                m = _BULLET_RE.match(candidate)
                if not m:
                    break
                items.append(m.group(1).strip())
                i += 1
            blocks.append(ContentBlock(kind="bullet_list", items=items))
            continue

        # ------------------------------------------------------------------
        # Numbered list block
        # ------------------------------------------------------------------
        numbered_match = _NUMBERED_RE.match(stripped)
        if numbered_match:
            items: list[str] = []
            while i < len(lines):
                candidate = _unwrap_decorative_line(lines[i]).strip()
                m = _NUMBERED_RE.match(candidate)
                if not m:
                    break
                items.append(m.group(1).strip())
                i += 1
            blocks.append(ContentBlock(kind="numbered_list", items=items))
            continue

        # ------------------------------------------------------------------
        # Paragraph block
        # ------------------------------------------------------------------
        start = i
        i += 1
        while i < len(lines):
            nxt = _unwrap_decorative_line(lines[i]).strip()
            if not nxt:
                break
            if _HEADING_RE.match(nxt):
                break
            if _is_table_line(nxt):
                break
            if _HTML_TABLE_START_RE.search(nxt):
                break
            if _BULLET_RE.match(nxt):
                break
            if _NUMBERED_RE.match(nxt):
                break
            if _MD_IMAGE_INLINE_RE.search(nxt) or _MD_IMAGE_REF_RE.search(nxt) or _REF_STYLE_IMAGE_ID_RE.search(nxt):
                break
            i += 1

        para_lines = [_unwrap_decorative_line(ln).rstrip() for ln in lines[start:i]]
        para = "\n".join(para_lines).strip()
        if para:
            blocks.append(ContentBlock(kind="paragraph", text=para))

    return blocks
```

#### `backend/modules/export/docx_builder.py`

**Language hint:** `python`

```python
"""Build a fresh DOCX from StyleMap + assembled sections (inbuilt templates)."""
from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

from modules.assembly.models import AssembledDocument
from modules.export.content_blocks import ContentBlock, parse_content_blocks
from modules.template.models import StyleMap


# Fixed diagram display box (requested final-polish behavior)
FIXED_DIAGRAM_WIDTH_IN = 5.8
FIXED_DIAGRAM_HEIGHT_IN = 3.4

# Default non-diagram image width
DEFAULT_IMAGE_WIDTH_IN = 5.5


def _apply_run_style(
    run,
    *,
    font_name: str,
    font_size_pt: int,
    bold: bool = False,
    italic: bool = False,
) -> None:
    run.font.name = font_name
    run.font.size = Pt(font_size_pt)
    run.font.bold = bold
    run.font.italic = italic


def _apply_paragraph_alignment(paragraph, alignment: str) -> None:
    value = (alignment or "").strip().lower()
    if value == "center":
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    elif value == "right":
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
    else:
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT


def _apply_body_style(paragraph, sm: StyleMap) -> None:
    for run in paragraph.runs:
        _apply_run_style(
            run,
            font_name=sm.body.font_name,
            font_size_pt=sm.body.font_size_pt,
            bold=sm.body.bold,
            italic=sm.body.italic,
        )
    _apply_paragraph_alignment(paragraph, sm.body.alignment)


def _apply_heading_style(paragraph, sm: StyleMap, level: int) -> None:
    style_cfg = sm.heading_1 if level <= 1 else sm.heading_2
    for run in paragraph.runs:
        _apply_run_style(
            run,
            font_name=style_cfg.font_name,
            font_size_pt=style_cfg.font_size_pt,
            bold=style_cfg.bold,
            italic=style_cfg.italic,
        )
    _apply_paragraph_alignment(paragraph, style_cfg.alignment)


def _apply_caption_style(paragraph, sm: StyleMap) -> None:
    for run in paragraph.runs:
        _apply_run_style(
            run,
            font_name=sm.body.font_name,
            font_size_pt=max(sm.body.font_size_pt - 1, 9),
            bold=False,
            italic=True,
        )
    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER


def _heading_style_name(level: int) -> str:
    if level <= 1:
        return "Heading 1"
    if level == 2:
        return "Heading 2"
    if level == 3:
        return "Heading 3"
    return "Heading 4"


def _normalize_heading_text(value: str) -> str:
    import re
    import unicodedata

    text = unicodedata.normalize("NFKC", value or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"^(?:\\)?#{1,6}\s+", "", text)
    text = re.sub(
        r"^(?:[a-z]\.|(?:\d+(?:\.\d+)*)[.)]?)\s+",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _normalize_image_target_key(value: str | None) -> str | None:
    if not value:
        return None
    return str(Path(value)).replace("\\", "/").strip().lower()


def _add_toc(doc: Document) -> None:
    """
    Insert a Word TOC field.
    Word updates the TOC on open / field update.
    """
    p = doc.add_paragraph()
    p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
    run = p.add_run()

    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")

    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = r'TOC \o "1-3" \h \z \u'

    fld_separate = OxmlElement("w:fldChar")
    fld_separate.set(qn("w:fldCharType"), "separate")

    fld_text = OxmlElement("w:t")
    fld_text.text = "Table of Contents"

    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")

    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_separate)
    run._r.append(fld_text)
    run._r.append(fld_end)


def _apply_page_setup(doc: Document, style_map: StyleMap) -> None:
    ps = getattr(style_map, "page_setup", None)
    if ps is None:
        return

    section = doc.sections[0]

    for attr_name, target_attr in (
        ("margin_left_in", "left_margin"),
        ("margin_right_in", "right_margin"),
        ("margin_top_in", "top_margin"),
        ("margin_bottom_in", "bottom_margin"),
    ):
        value = getattr(ps, attr_name, None)
        if value is not None:
            setattr(section, target_attr, Inches(float(value)))

    orientation = getattr(ps, "orientation", None)
    if isinstance(orientation, str) and orientation.strip().lower() == "landscape":
        from docx.enum.section import WD_ORIENT

        section.orientation = WD_ORIENT.LANDSCAPE
        width = section.page_height
        height = section.page_width
        section.page_width = width
        section.page_height = height


class DocxBuilder:
    def __init__(self, storage_root: Path) -> None:
        self._storage_root = storage_root
        self._figure_counter = 0

    def build(self, assembled: AssembledDocument, style_map: StyleMap, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc = Document()
        _apply_page_setup(doc, style_map)

        # Title
        title_para = doc.add_paragraph(assembled.title)
        try:
            title_para.style = doc.styles["Title"]
        except (KeyError, ValueError):
            pass

        for run in title_para.runs:
            _apply_run_style(
                run,
                font_name=style_map.heading_1.font_name,
                font_size_pt=max(style_map.heading_1.font_size_pt + 2, 18),
                bold=True,
                italic=False,
            )
        title_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        # TOC
        _add_toc(doc)
        doc.add_paragraph("")

        # Content
        for idx, section in enumerate(assembled.sections):
            heading = doc.add_paragraph(section.title)
            try:
                heading.style = doc.styles[_heading_style_name(section.level)]
            except (KeyError, ValueError):
                try:
                    heading.style = doc.styles["Heading 1"]
                except (KeyError, ValueError):
                    pass
            _apply_heading_style(heading, style_map, level=section.level)

            diagram_rendered = False
            if section.output_type == "diagram" and section.diagram_path:
                img = self._resolve_image_path(section.diagram_path)
                if img and img.exists():
                    self._insert_image_with_caption(
                        doc=doc,
                        image_path=img,
                        caption=f"Figure {self._next_figure_number()}: {section.title}",
                        style_map=style_map,
                        fixed_diagram_size=True,
                    )
                    diagram_rendered = True

            blocks = section.content_blocks or [b.__dict__ for b in parse_content_blocks(section.content)]
            self._add_body_blocks(
                doc=doc,
                section_title=section.title,
                blocks=blocks,
                style_map=style_map,
                suppress_image_target=_normalize_image_target_key(section.diagram_path) if diagram_rendered else None,
                suppress_all_image_blocks=diagram_rendered and section.output_type == "diagram",
                diagram_section=(section.output_type == "diagram"),
            )

            if idx < len(assembled.sections) - 1:
                doc.add_paragraph("")

        doc.save(str(output_path))

    def _add_body_blocks(
        self,
        doc: Document,
        *,
        section_title: str,
        blocks: list[dict[str, object]],
        style_map: StyleMap,
        suppress_image_target: str | None = None,
        suppress_all_image_blocks: bool = False,
        diagram_section: bool = False,
    ) -> None:
        for raw_block in blocks:
            block = self._coerce_block(raw_block)
            if block is None:
                continue

            if block.kind == "heading":
                if _normalize_heading_text(block.text) == _normalize_heading_text(section_title):
                    continue
                para = doc.add_paragraph(block.text)
                try:
                    para.style = doc.styles[_heading_style_name(max(block.level, 2))]
                except (KeyError, ValueError):
                    try:
                        para.style = doc.styles["Heading 2"]
                    except (KeyError, ValueError):
                        pass
                _apply_heading_style(para, style_map, level=2 if block.level <= 2 else 3)
                continue

            if block.kind == "paragraph":
                para = doc.add_paragraph(block.text)
                try:
                    para.style = doc.styles["Normal"]
                except (KeyError, ValueError):
                    pass
                _apply_body_style(para, style_map)
                continue

            if block.kind == "bullet_list":
                for item in block.items:
                    try:
                        para = doc.add_paragraph(item, style="List Bullet")
                    except (KeyError, ValueError):
                        para = doc.add_paragraph(f"• {item}")
                    _apply_body_style(para, style_map)
                continue

            if block.kind == "numbered_list":
                for index, item in enumerate(block.items, start=1):
                    try:
                        para = doc.add_paragraph(item, style="List Number")
                    except (KeyError, ValueError):
                        para = doc.add_paragraph(f"{index}. {item}")
                    _apply_body_style(para, style_map)
                continue

            if block.kind in {"table_gfm", "table_html"}:
                if not block.rows:
                    continue

                cols = max(len(row) for row in block.rows)
                if cols <= 0:
                    continue

                table = doc.add_table(rows=len(block.rows), cols=cols)
                table.style = "Table Grid"

                for r_idx, row in enumerate(block.rows):
                    for c_idx in range(cols):
                        cell = table.cell(r_idx, c_idx)
                        value = row[c_idx] if c_idx < len(row) else ""
                        cell.text = str(value)

                        for para in cell.paragraphs:
                            for run in para.runs:
                                _apply_run_style(
                                    run,
                                    font_name=style_map.body.font_name,
                                    font_size_pt=style_map.body.font_size_pt,
                                    bold=(r_idx == 0),
                                    italic=False,
                                )
                continue

            if block.kind == "image":
                if suppress_all_image_blocks:
                    continue

                target_key = _normalize_image_target_key(block.image_target)
                if suppress_image_target and target_key == suppress_image_target:
                    continue

                image_path = self._resolve_image_path(block.image_target)
                if image_path and image_path.exists():
                    alt = block.image_alt or section_title
                    self._insert_image_with_caption(
                        doc=doc,
                        image_path=image_path,
                        caption=f"Figure {self._next_figure_number()}: {alt}",
                        style_map=style_map,
                        fixed_diagram_size=diagram_section,
                    )
                continue

            if block.kind == "caption":
                continue

    def _insert_image_with_caption(
        self,
        *,
        doc: Document,
        image_path: Path,
        caption: str,
        style_map: StyleMap,
        fixed_diagram_size: bool = False,
    ) -> None:
        pic_para = doc.add_paragraph()
        pic_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        run = pic_para.add_run()

        if fixed_diagram_size:
            run.add_picture(
                str(image_path),
                width=Inches(FIXED_DIAGRAM_WIDTH_IN),
                height=Inches(FIXED_DIAGRAM_HEIGHT_IN),
            )
        else:
            run.add_picture(
                str(image_path),
                width=Inches(DEFAULT_IMAGE_WIDTH_IN),
            )

        caption_para = doc.add_paragraph(caption)
        try:
            caption_para.style = doc.styles["Caption"]
        except (KeyError, ValueError):
            try:
                caption_para.style = doc.styles["Normal"]
            except (KeyError, ValueError):
                pass
        _apply_caption_style(caption_para, style_map)

    def _resolve_image_path(self, image_target: str | None) -> Path | None:
        if not image_target:
            return None

        target = Path(image_target)
        if target.is_absolute():
            return target

        direct = self._storage_root / target
        if direct.exists():
            return direct

        candidate = self._storage_root / "outputs" / target
        if candidate.exists():
            return candidate

        candidate = self._storage_root / "diagrams" / target
        if candidate.exists():
            return candidate

        return None

    def _next_figure_number(self) -> int:
        self._figure_counter += 1
        return self._figure_counter

    def _coerce_block(self, raw_block: dict[str, object]) -> ContentBlock | None:
        try:
            kind = str(raw_block.get("kind") or "").strip()
            if not kind:
                return None

            return ContentBlock(
                kind=kind,  # type: ignore[arg-type]
                text=str(raw_block.get("text") or ""),
                level=int(raw_block.get("level") or 0),
                items=[str(v) for v in (raw_block.get("items") or [])]
                if isinstance(raw_block.get("items"), list)
                else [],
                rows=[
                    [str(cell) for cell in row]
                    for row in (raw_block.get("rows") or [])
                ]
                if isinstance(raw_block.get("rows"), list)
                else [],
                image_target=str(raw_block.get("image_target"))
                if raw_block.get("image_target") is not None
                else None,
                image_alt=str(raw_block.get("image_alt"))
                if raw_block.get("image_alt") is not None
                else None,
            )
        except Exception:
            return None
```

#### `backend/modules/export/docx_filler.py`

**Language hint:** `python`

```python
"""Fill a custom DOCX template with assembled section content."""

from __future__ import annotations

import re
import unicodedata
from copy import deepcopy
from pathlib import Path
from dataclasses import asdict

from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml import OxmlElement
from docx.shared import Inches, Pt
from docx.text.paragraph import Paragraph

from core.ids import utc_now_iso
from modules.assembly.models import AssembledDocument
from modules.export.content_blocks import ContentBlock, parse_content_blocks
from modules.template.models import StyleMap

# Fixed diagram display box (requested final-polish behavior)
FIXED_DIAGRAM_WIDTH_IN = 5.8
FIXED_DIAGRAM_HEIGHT_IN = 3.4

# Default non-diagram image width
DEFAULT_IMAGE_WIDTH_IN = 5.5


def _heading_level(paragraph: Paragraph) -> int | None:
    style_name = paragraph.style.name if paragraph.style else ""
    if not style_name.startswith("Heading"):
        return None
    parts = style_name.split()
    try:
        return int(parts[-1])
    except (ValueError, IndexError):
        return 1


def _is_heading_like(paragraph: Paragraph) -> bool:
    if _heading_level(paragraph) is not None:
        return True

    style_name = paragraph.style.name if paragraph.style else ""
    if style_name and "heading" in style_name.lower():
        return True

    text = paragraph.text.strip()
    if not text:
        return False

    if text.isupper() and len(text.split()) <= 12:
        return True

    return False


def _insert_paragraph_after(paragraph: Paragraph, text: str = "", style: object | None = None) -> Paragraph:
    new_p = OxmlElement("w:p")
    paragraph._p.addnext(new_p)  # type: ignore[attr-defined]
    new_para = Paragraph(new_p, paragraph._parent)  # type: ignore[arg-type]
    if text:
        new_para.add_run(text)
    if style is not None:
        new_para.style = style
    return new_para


def _clear_following_until_heading(doc: Document, heading: Paragraph) -> None:
    el = heading._p
    nxt = el.getnext()
    while nxt is not None:
        if nxt.tag.endswith("p"):
            para = Paragraph(nxt, doc)
            if _heading_level(para) is not None:
                break
        nxt_next = nxt.getnext()
        parent = nxt.getparent()
        if parent is not None:
            parent.remove(nxt)
        nxt = nxt_next


def _normalize_heading_text(value: str) -> str:
    text = unicodedata.normalize("NFKC", value or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(
        r"^(?:[a-z]\.|(?:\d+(?:\.\d+)*)[.)]?)\s+",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"^(?:\\)?#{1,6}\s+", "", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _heading_match_score(template_heading: str, section_title: str) -> int:
    raw_template = (template_heading or "").strip()
    raw_target = (section_title or "").strip()
    if not raw_template or not raw_target:
        return -1

    if raw_template == raw_target:
        return 100

    norm_template = _normalize_heading_text(raw_template)
    norm_target = _normalize_heading_text(raw_target)
    if not norm_template or not norm_target:
        return -1

    if norm_template == norm_target:
        return 90

    if norm_template in norm_target or norm_target in norm_template:
        shorter = min(len(norm_template), len(norm_target))
        if shorter >= 6:
            return 70

    return -1


def _find_best_heading_paragraph(
    doc: Document,
    section_title: str,
    used_heading_elements: set[int],
) -> Paragraph | None:
    best_para: Paragraph | None = None
    best_score = -1

    for p in doc.paragraphs:
        if id(p._p) in used_heading_elements:
            continue

        text = p.text.strip()
        if not text:
            continue

        score = _heading_match_score(text, section_title)
        if score < 0:
            continue

        if _is_heading_like(p):
            score += 5

        if score > best_score:
            best_score = score
            best_para = p
            if best_score >= 100:
                break

    return best_para


def _apply_run_style(
    run,
    *,
    font_name: str,
    font_size_pt: int,
    bold: bool = False,
    italic: bool = False,
) -> None:
    run.font.name = font_name
    run.font.size = Pt(font_size_pt)
    run.font.bold = bold
    run.font.italic = italic


def _apply_paragraph_alignment(paragraph: Paragraph, alignment: str) -> None:
    value = (alignment or "").strip().lower()
    if value == "center":
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    elif value == "right":
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
    else:
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT


def _apply_body_style(paragraph: Paragraph, sm: StyleMap) -> None:
    for run in paragraph.runs:
        _apply_run_style(
            run,
            font_name=sm.body.font_name,
            font_size_pt=sm.body.font_size_pt,
            bold=sm.body.bold,
            italic=sm.body.italic,
        )
    _apply_paragraph_alignment(paragraph, sm.body.alignment)


def _apply_heading_style(paragraph: Paragraph, sm: StyleMap, level: int) -> None:
    style_cfg = sm.heading_1 if level <= 1 else sm.heading_2
    for run in paragraph.runs:
        _apply_run_style(
            run,
            font_name=style_cfg.font_name,
            font_size_pt=style_cfg.font_size_pt,
            bold=style_cfg.bold,
            italic=style_cfg.italic,
        )
    _apply_paragraph_alignment(paragraph, style_cfg.alignment)


def _apply_caption_style(paragraph: Paragraph, sm: StyleMap) -> None:
    for run in paragraph.runs:
        _apply_run_style(
            run,
            font_name=sm.body.font_name,
            font_size_pt=max(sm.body.font_size_pt - 1, 9),
            bold=False,
            italic=True,
        )
    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER


def _add_line_after_doc(
    doc: Document,
    after: Paragraph,
    line: str,
    normal,
    sm: StyleMap,
) -> Paragraph:
    stripped = line.strip()
    if not stripped:
        return after

    bullet_prefixes = ("- ", "* ", "• ")
    numbered = re.match(r"^(\d+[.)])\s+", stripped)

    ref = _insert_paragraph_after(after, "", normal)

    for bp in bullet_prefixes:
        if stripped.startswith(bp):
            text = stripped[len(bp):].strip()
            try:
                ref.style = doc.styles["List Bullet"]
                if text:
                    ref.add_run(text)
            except (KeyError, ValueError):
                ref.add_run(f"• {text}")
            _apply_body_style(ref, sm)
            return ref

    if numbered:
        text = stripped[numbered.end():].strip()
        try:
            ref.style = doc.styles["List Number"]
            if text:
                ref.add_run(text)
        except (KeyError, ValueError):
            ref.add_run(stripped)
        _apply_body_style(ref, sm)
        return ref

    out = _insert_paragraph_after(after, stripped, normal)
    _apply_body_style(out, sm)
    return out


def _build_table_element(rows: list[list[str]], sm: StyleMap):
    scratch = Document()
    cols = max(len(r) for r in rows)
    table = scratch.add_table(rows=len(rows), cols=cols)
    table.style = "Table Grid"

    for r_idx, row in enumerate(rows):
        for c_idx in range(cols):
            cell = table.cell(r_idx, c_idx)
            val = row[c_idx] if c_idx < len(row) else ""
            cell.text = val
            for para in cell.paragraphs:
                for run in para.runs:
                    run.font.size = Pt(sm.body.font_size_pt)
                    run.font.name = sm.body.font_name
                    if r_idx == 0:
                        run.font.bold = True

    return deepcopy(table._tbl)


def _normalize_image_target_key(value: str | None) -> str | None:
    if not value:
        return None
    return str(Path(value)).replace("\\", "/").strip().lower()


class DocxFiller:
    def __init__(self, storage_root: Path) -> None:
        self._storage_root = storage_root
        self._figure_counter = 0

    def fill(
        self,
        template_path: Path,
        assembled: AssembledDocument,
        output_path: Path,
        *,
        style_map: StyleMap | None = None,
    ) -> list[dict[str, object]]:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc = Document(str(template_path))
        used_heading_elements: set[int] = set()
        warnings: list[dict[str, object]] = []
        sm = style_map or StyleMap()
        ts = utc_now_iso()
        normal = doc.styles["Normal"]

        for section in assembled.sections:
            heading = _find_best_heading_paragraph(doc, section.title, used_heading_elements)
            if heading is None:
                warnings.append(
                    {
                        "phase": "RENDER_EXPORT",
                        "code": "template_heading_not_found",
                        "section_id": section.section_id,
                        "title": section.title,
                        "message": (
                            f"No paragraph matching heading {section.title!r} in template; "
                            "section content was not inserted."
                        ),
                        "at": ts,
                    },
                )
                continue

            used_heading_elements.add(id(heading._p))
            _clear_following_until_heading(doc, heading)
            ref: Paragraph = heading

            diagram_rendered = False
            if section.output_type == "diagram" and section.diagram_path:
                img = self._storage_root / Path(section.diagram_path)
                if img.exists():
                    ref = self._insert_image_with_caption(
                        doc=doc,
                        after=ref,
                        image_path=img,
                        caption=f"Figure {self._next_figure_number()}: {section.title}",
                        sm=sm,
                        normal=normal,
                        fixed_diagram_size=True,
                    )
                    diagram_rendered = True

            blocks = section.content_blocks or [asdict(b) for b in parse_content_blocks(section.content)]
            ref = self._append_blocks(
                doc=doc,
                after=ref,
                section_title=section.title,
                content_blocks=blocks,
                sm=sm,
                normal=normal,
                suppress_image_target=_normalize_image_target_key(section.diagram_path) if diagram_rendered else None,
                suppress_all_image_blocks=diagram_rendered and section.output_type == "diagram",
                diagram_section=(section.output_type == "diagram"),
            )

        doc.save(str(output_path))
        return warnings

    def _append_blocks(
        self,
        doc: Document,
        after: Paragraph,
        *,
        section_title: str,
        content_blocks: list[dict[str, object]],
        sm: StyleMap,
        normal,
        suppress_image_target: str | None = None,
        suppress_all_image_blocks: bool = False,
        diagram_section: bool = False,
    ) -> Paragraph:
        ref = after

        for raw_block in content_blocks:
            block = self._coerce_block(raw_block)
            if block is None:
                continue

            if block.kind == "heading":
                if _normalize_heading_text(block.text) == _normalize_heading_text(section_title):
                    continue
                ref = self._insert_heading_after(doc, ref, block.text, block.level, sm)
                continue

            if block.kind == "paragraph":
                para = _insert_paragraph_after(ref, block.text, normal)
                _apply_body_style(para, sm)
                ref = para
                continue

            if block.kind == "bullet_list":
                for item in block.items:
                    ref = _add_line_after_doc(doc, ref, f"- {item}", normal, sm)
                continue

            if block.kind == "numbered_list":
                for idx, item in enumerate(block.items, start=1):
                    ref = _add_line_after_doc(doc, ref, f"{idx}. {item}", normal, sm)
                continue

            if block.kind in {"table_gfm", "table_html"}:
                if not block.rows:
                    continue
                tbl_el = _build_table_element(block.rows, sm)
                ref._p.addnext(tbl_el)  # type: ignore[attr-defined]

                tail = OxmlElement("w:p")
                tbl_el.addnext(tail)
                ref = Paragraph(tail, doc)
                continue

            if block.kind == "image":
                if suppress_all_image_blocks:
                    continue

                target_key = _normalize_image_target_key(block.image_target)
                if suppress_image_target and target_key == suppress_image_target:
                    continue

                image_path = self._resolve_image_path(block.image_target)
                if image_path is None or not image_path.exists():
                    continue

                alt = block.image_alt or section_title
                ref = self._insert_image_with_caption(
                    doc=doc,
                    after=ref,
                    image_path=image_path,
                    caption=f"Figure {self._next_figure_number()}: {alt}",
                    sm=sm,
                    normal=normal,
                    fixed_diagram_size=diagram_section,
                )
                continue

            if block.kind == "caption":
                continue

        return ref

    def _insert_heading_after(
        self,
        doc: Document,
        after: Paragraph,
        text: str,
        level: int,
        sm: StyleMap,
    ) -> Paragraph:
        para = _insert_paragraph_after(after, text, None)
        style_name = "Heading 2" if level <= 2 else "Heading 3"
        try:
            para.style = doc.styles[style_name]
        except (KeyError, ValueError):
            para.style = doc.styles["Normal"]
        _apply_heading_style(para, sm, level=1 if level <= 2 else 2)
        return para

    def _insert_image_with_caption(
        self,
        *,
        doc: Document,
        after: Paragraph,
        image_path: Path,
        caption: str,
        sm: StyleMap,
        normal,
        fixed_diagram_size: bool = False,
    ) -> Paragraph:
        img_para = _insert_paragraph_after(after, "", normal)
        run = img_para.add_run()

        if fixed_diagram_size:
            run.add_picture(
                str(image_path),
                width=Inches(FIXED_DIAGRAM_WIDTH_IN),
                height=Inches(FIXED_DIAGRAM_HEIGHT_IN),
            )
        else:
            run.add_picture(
                str(image_path),
                width=Inches(DEFAULT_IMAGE_WIDTH_IN),
            )

        img_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        caption_para = _insert_paragraph_after(img_para, caption, None)
        try:
            caption_para.style = doc.styles["Caption"]
        except (KeyError, ValueError):
            caption_para.style = doc.styles["Normal"]
        _apply_caption_style(caption_para, sm)
        return caption_para

    def _next_figure_number(self) -> int:
        self._figure_counter += 1
        return self._figure_counter

    def _resolve_image_path(self, image_target: str | None) -> Path | None:
        if not image_target:
            return None

        target = Path(image_target)
        if target.is_absolute():
            return target

        direct = self._storage_root / target
        if direct.exists():
            return direct

        candidate = self._storage_root / "outputs" / target
        if candidate.exists():
            return candidate

        candidate = self._storage_root / "diagrams" / target
        if candidate.exists():
            return candidate

        return None

    def _coerce_block(self, raw_block) -> ContentBlock | None:
        try:
            if isinstance(raw_block, ContentBlock):
                return raw_block

            if not isinstance(raw_block, dict):
                return None

            kind = str(raw_block.get("kind") or "").strip()
            if not kind:
                return None

            text = str(raw_block.get("text") or "")
            level = int(raw_block.get("level") or 0)

            raw_items = raw_block.get("items") or []
            items = [str(item) for item in raw_items] if isinstance(raw_items, list) else []

            raw_rows = raw_block.get("rows") or []
            rows: list[list[str]] = []
            if isinstance(raw_rows, list):
                for row in raw_rows:
                    if isinstance(row, list):
                        rows.append([str(cell) for cell in row])

            image_target = raw_block.get("image_target")
            image_alt = raw_block.get("image_alt")

            return ContentBlock(
                kind=kind,  # type: ignore[arg-type]
                text=text,
                level=level,
                items=items,
                rows=rows,
                image_target=str(image_target) if image_target is not None else None,
                image_alt=str(image_alt) if image_alt is not None else None,
            )
        except Exception:
            return None
```

#### `backend/modules/export/markdown_tables.py`

**Language hint:** `python`

```python
"""Compatibility layer for markdown/table parsing plus semantic content blocks."""
from __future__ import annotations

from typing import Literal

from modules.export.content_blocks import (
    ContentBlock,
    parse_content_blocks,
    parse_gfm_table,
    parse_html_table,
)

BlockKind = Literal["text", "table"]

def _rows_to_pipe_table(rows: list[list[str]]) -> str:
    """
    Convert parsed rows into a clean GitHub-flavored markdown pipe table string.
    """
    if not rows:
        return ""

    header = rows[0]
    header_line = "| " + " | ".join(str(cell) for cell in header) + " |"
    separator_line = "| " + " | ".join("---" for _ in header) + " |"

    lines = [header_line, separator_line]

    for row in rows[1:]:
        normalized_row = [str(cell) for cell in row]
        lines.append("| " + " | ".join(normalized_row) + " |")

    return "\n".join(lines)


def split_markdown_blocks(content: str) -> list[tuple[BlockKind, str]]:
    """
    Backward-compatible API used by current builder/filler/xlsx code.

    Notes:
    - headings, images, captions, lists, and HTML tables are detected by the
      richer semantic parser, but for backward compatibility this function maps:
        * gfm/html tables -> ("table", normalized table text)
        * everything else -> ("text", plain text payload)
    """
    blocks = parse_content_blocks(content)
    out: list[tuple[BlockKind, str]] = []

    for block in blocks:
        if block.kind in {"table_gfm", "table_html"}:
            normalized = block.text or _rows_to_pipe_table(block.rows)
            if block.rows:
                normalized = _rows_to_pipe_table(block.rows)
            out.append(("table", normalized))
            continue

        if block.kind == "heading":
            hashes = "#" * max(block.level, 1)
            out.append(("text", f"{hashes} {block.text}".strip()))
            continue

        if block.kind == "bullet_list":
            out.append(("text", "\n".join(f"- {item}" for item in block.items)))
            continue

        if block.kind == "numbered_list":
            out.append(("text", "\n".join(f"{idx + 1}. {item}" for idx, item in enumerate(block.items))))
            continue

        if block.kind == "image":
            payload = block.text or (block.image_target or "")
            out.append(("text", payload))
            continue

        if block.kind == "caption":
            out.append(("text", block.text))
            continue

        # paragraph and any fallback kinds
        out.append(("text", block.text))

    return out


__all__ = [
    "ContentBlock",
    "BlockKind",
    "parse_content_blocks",
    "parse_gfm_table",
    "parse_html_table",
    "split_markdown_blocks",
]
```

#### `backend/modules/export/renderer.py`

**Language hint:** `python`

```python
"""Route assembled documents to the correct file builder."""
from __future__ import annotations

from pathlib import Path

from core.constants import DocType, TemplateSource
from modules.assembly.models import AssembledDocument, AssembledSection
from modules.assembly.normalizer import normalize_section_content
from modules.export.docx_builder import DocxBuilder
from modules.export.docx_filler import DocxFiller
from modules.export.types import ExportDocumentInfo, ExportTemplateInfo
from modules.export.xlsx_builder import XlsxBuilder
from modules.template.inbuilt.registry import is_inbuilt_template_id
from modules.template.models import StyleMap


class ExportRenderer:
    def __init__(self, storage_root: Path) -> None:
        self._storage_root = storage_root
        self._docx_builder = DocxBuilder(storage_root)
        self._docx_filler = DocxFiller(storage_root)
        self._xlsx = XlsxBuilder()

    def render(
        self,
        *,
        workflow_run_id: str,
        document: ExportDocumentInfo,
        template: ExportTemplateInfo,
        assembled: AssembledDocument,
        style_map: StyleMap,
        sheet_map: dict[str, object] | None = None,
        export_mode: str | None = None,
    ) -> tuple[Path, str, list[dict[str, object]]]:
        outputs = self._storage_root / "outputs"
        outputs.mkdir(parents=True, exist_ok=True)

        stem = Path(document.filename).stem
        friendly_doc = f"{stem}_{assembled.doc_type}"

        export_warnings: list[dict[str, object]] = []

        mode = (export_mode or assembled.export_mode or "final").strip().lower()
        assembled_for_export = self._prepare_document_for_export(
            assembled=assembled,
            export_mode=mode,
            export_warnings=export_warnings,
        )

        if assembled_for_export.doc_type == DocType.UAT.value:
            out = outputs / f"{workflow_run_id}.xlsx"
            tpl: Path | None = None
            if template.file_path:
                cand = self._storage_root / "templates" / Path(template.file_path)
                if cand.is_file():
                    tpl = cand

            self._xlsx.build(
                assembled_for_export,
                out,
                template_path=tpl,
                sheet_map=sheet_map,
            )
            return out, f"{friendly_doc}.xlsx", export_warnings

        out = outputs / f"{workflow_run_id}.docx"

        use_inbuilt = (
            template.template_source == TemplateSource.INBUILT
            or is_inbuilt_template_id(template.template_id)
        )
        if use_inbuilt:
            self._docx_builder.build(assembled_for_export, style_map, out)
            return out, f"{friendly_doc}.docx", export_warnings

        custom_tpl: Path | None = None
        if template.file_path:
            cand = self._storage_root / "templates" / Path(template.file_path)
            if cand.is_file():
                custom_tpl = cand

        if custom_tpl is not None:
            export_warnings.extend(
                self._docx_filler.fill(custom_tpl, assembled_for_export, out, style_map=style_map),
            )
            return out, f"{friendly_doc}.docx", export_warnings

        self._docx_builder.build(assembled_for_export, style_map, out)
        return out, f"{friendly_doc}.docx", export_warnings

    def _prepare_document_for_export(
        self,
        *,
        assembled: AssembledDocument,
        export_mode: str,
        export_warnings: list[dict[str, object]],
    ) -> AssembledDocument:
        """
        Final safety-pass before rendering.

        Why this exists:
        - Assembly should already normalize content, but export should still enforce
          final-mode stripping so internal drafting content does not leak into deliverables
          if upstream content arrives unclean.
        """
        if export_mode != "final":
            return assembled

        cleaned_sections: list[AssembledSection] = []
        child_map = self._build_child_title_map(assembled)

        for section in assembled.sections:
            if section.output_type == "diagram":
                if not section.diagram_path:
                    export_warnings.append(
                        {
                            "phase": "RENDER_EXPORT",
                            "code": "diagram_path_missing",
                            "section_id": section.section_id,
                            "title": section.title,
                            "message": (
                                f"Diagram section {section.title!r} reached export without a diagram_path; "
                                "the final DOCX may show only the heading."
                            ),
                        },
                    )
                cleaned_sections.append(
                    section.model_copy(
                        update={
                            "export_mode": "final",
                        }
                    )
                )
                continue

            normalized = normalize_section_content(
                section_title=section.title,
                content=section.content or "",
                child_titles=child_map.get(section.section_id, []),
                export_mode="final",
            )
            cleaned_sections.append(
                section.model_copy(
                    update={
                        "content": normalized.content,
                        "export_mode": "final",
                    }
                )
            )

        return assembled.model_copy(
            update={
                "sections": cleaned_sections,
                "export_mode": "final",
            }
        )

    def _build_child_title_map(self, assembled: AssembledDocument) -> dict[str, list[str]]:
        """
        Reconstruct child-title visibility from assembled section ordering + levels.
        """
        child_map: dict[str, list[str]] = {}
        sections = assembled.sections

        for idx, current in enumerate(sections):
            child_titles: list[str] = []
            current_level = int(current.level)

            for next_section in sections[idx + 1:]:
                next_level = int(next_section.level)
                if next_level <= current_level:
                    break
                child_titles.append(next_section.title)

            child_map[current.section_id] = child_titles

        return child_map
```

#### `backend/modules/export/types.py`

**Language hint:** `python`

```python
"""Export inputs decoupled from repository models (layering)."""

from __future__ import annotations

from typing import NamedTuple


class ExportDocumentInfo(NamedTuple):
    filename: str


class ExportTemplateInfo(NamedTuple):
    template_id: str
    template_source: str
    file_path: str | None
```

#### `backend/modules/export/xlsx_builder.py`

**Language hint:** `python`

```python
"""Build or fill UAT XLSX outputs."""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.utils import get_column_letter

from modules.assembly.models import AssembledDocument
from modules.export.markdown_tables import parse_gfm_table, split_markdown_blocks


def _sheet_title(title: str) -> str:
    t = title.strip()[:31]
    return t or "Sheet"


def _get_or_create_worksheet(wb, section_title: str, sheet_map: dict[str, object] | None):
    """Resolve sheet using workbook names first, then template sheet_map entries."""
    st_full = section_title.strip()
    st_short = _sheet_title(st_full)

    def matches(sheet_name: str) -> bool:
        sn = sheet_name.strip()
        return sn == st_full or sn == st_short or sn.lower() == st_full.lower()

    for sn in wb.sheetnames:
        if matches(sn):
            return wb[sn]

    if sheet_map and isinstance(sheet_map.get("sheets"), list):
        for item in sheet_map["sheets"]:
            nm = (item.get("name") or "").strip()
            if not nm:
                continue
            if nm == st_full or nm.lower() == st_full.lower() or nm == st_short:
                if nm in wb.sheetnames:
                    return wb[nm]
                n2 = _sheet_title(nm)
                if n2 in wb.sheetnames:
                    return wb[n2]

    new_name = st_short
    if new_name not in wb.sheetnames:
        wb.create_sheet(title=new_name)
    return wb[new_name]


class XlsxBuilder:
    def build(
        self,
        assembled: AssembledDocument,
        output_path: Path,
        *,
        template_path: Path | None = None,
        sheet_map: dict[str, object] | None = None,
    ) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        from_template = bool(template_path and template_path.is_file())
        if from_template:
            from openpyxl import load_workbook

            wb = load_workbook(template_path)  # type: ignore[arg-type]
        else:
            wb = Workbook()
            wb.remove(wb.active)

        for section in assembled.sections:
            ws = _get_or_create_worksheet(wb, section.title, sheet_map)
            mr = ws.max_row or 0
            mc = ws.max_column or 0

            if from_template:
                header_nonempty = mr >= 1 and any(
                    ws.cell(row=1, column=c).value not in (None, "")
                    for c in range(1, mc + 1)
                )
                if mr > 1:
                    ws.delete_rows(2, mr - 1)
                elif mr == 1 and not header_nonempty:
                    ws.delete_rows(1, 1)
                start_row = 2 if header_nonempty else 1
            else:
                if mr > 0:
                    ws.delete_rows(1, mr)
                start_row = 1

            rows: list[list[str]] = []
            if section.output_type == "table":
                for kind, payload in split_markdown_blocks(section.content):
                    if kind == "table":
                        rows.extend(parse_gfm_table(payload))
            if not rows and section.content.strip():
                rows = [[section.content.strip()]]

            for r_off, row in enumerate(rows):
                r_idx = start_row + r_off
                for c_idx, val in enumerate(row, start=1):
                    ws.cell(row=r_idx, column=c_idx, value=val)
                    if r_off == 0:
                        ws.column_dimensions[get_column_letter(c_idx)].width = min(
                            max(len(str(val)) + 2, 12),
                            48,
                        )

        wb.save(str(output_path))
```

#### `backend/modules/generation/__init__.py`

**Language hint:** `python`

```python
"""Generation phase: prompts, LLM calls, diagram rendering."""

from __future__ import annotations

from modules.generation.cost_tracking import (
    GenerationCostTracker,
    GenerationCostSnapshot,
    llm_delta_between_snapshots,
)
from modules.generation.diagram_generator import DiagramSectionGenerator, extract_mermaid, extract_plantuml
from modules.generation.kroki import KrokiRenderer
from modules.generation.models import GenerationSectionResult
from modules.generation.observability import merge_generation_observability
from modules.generation.orchestrator import GenerationOrchestrator, compute_execution_waves
from modules.generation.prompt_loader import GenerationPromptLoader
from modules.generation.table_generator import TableSectionGenerator
from modules.generation.text_generator import TextSectionGenerator

__all__ = [
    "GenerationCostSnapshot",
    "GenerationCostTracker",
    "GenerationOrchestrator",
    "GenerationPromptLoader",
    "GenerationSectionResult",
    "DiagramSectionGenerator",
    "KrokiRenderer",
    "TableSectionGenerator",
    "TextSectionGenerator",
    "compute_execution_waves",
    "extract_mermaid",
    "extract_plantuml",
    "llm_delta_between_snapshots",
    "merge_generation_observability",
]
```

#### `backend/modules/generation/context.py`

**Language hint:** `python`

```python
"""Shared prompt context builders for generation."""
from __future__ import annotations

from collections.abc import Iterable

from modules.template.models import SectionDefinition

_NO_EVIDENCE_TEXT = (
    "No retrieved evidence is available for this section. "
    "Rely on the section title and description only."
)


def _normalize_text(value: object) -> str:
    return str(value or "").strip()


def _truncate_text(text: str, *, max_chars: int | None = None) -> str:
    if max_chars is None or max_chars <= 0:
        return text
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars].rstrip()
    return f"{truncated}\n\n[truncated for prompt budget]"


def evidence_text_from_retrieval(
    payload: dict[str, object] | None,
    *,
    max_chars: int | None = None,
) -> str:
    if not payload:
        return _NO_EVIDENCE_TEXT

    raw = payload.get("context_text")
    text = _normalize_text(raw)
    if not text:
        return _NO_EVIDENCE_TEXT

    return _truncate_text(text, max_chars=max_chars)


def citations_from_retrieval(payload: dict[str, object] | None) -> list[dict[str, object]]:
    if not payload:
        return []

    raw = payload.get("citations")
    if not isinstance(raw, list):
        return []

    out: list[dict[str, object]] = []
    for item in raw:
        if isinstance(item, dict):
            out.append(dict(item))
    return out


def format_table_headers(section: SectionDefinition) -> str:
    if section.table_headers:
        return " | ".join(section.table_headers)
    if section.required_fields:
        return " | ".join(section.required_fields)
    return "Item | Details | Evidence"


def format_required_fields(section: SectionDefinition) -> str:
    if section.required_fields:
        return ", ".join(section.required_fields)
    return "N/A"


def format_child_titles(child_titles: Iterable[str] | None) -> str:
    values = [str(title).strip() for title in (child_titles or []) if str(title).strip()]
    if not values:
        return "None"
    return ", ".join(values)


def infer_section_role(*, parent_title: str | None, child_titles: Iterable[str] | None) -> str:
    has_parent = bool((parent_title or "").strip())
    has_children = any(str(title).strip() for title in (child_titles or []))

    if has_children:
        return "parent_with_children"
    if has_parent:
        return "child_or_leaf"
    return "standalone_or_top_level"


def build_prompt_mapping(
    section: SectionDefinition,
    doc_type: str,
    evidence_context: str,
    *,
    render_error: str = "",
    failed_diagram_source: str = "",
    parent_section_title: str = "",
    child_section_titles: Iterable[str] | None = None,
) -> dict[str, str]:
    child_titles_text = format_child_titles(child_section_titles)
    section_role = infer_section_role(
        parent_title=parent_section_title,
        child_titles=child_section_titles,
    )

    return {
        "doc_type": doc_type,
        "section_title": section.title,
        "section_description": section.description,
        "generation_hints": section.generation_hints or "N/A",
        "expected_length": section.expected_length,
        "tone": section.tone,
        "evidence_context": evidence_context,
        "table_headers": format_table_headers(section),
        "required_fields": format_required_fields(section),
        "render_error": render_error,
        "failed_diagram_source": failed_diagram_source,
        "parent_section_title": (parent_section_title or "").strip() or "None",
        "child_section_titles": child_titles_text,
        "section_role": section_role,
    }
```

#### `backend/modules/generation/cost_tracking.py`

**Language hint:** `python`

```python
"""Per-workflow generation phase LLM cost tracking (mirrors retrieval tracker pattern)."""

from __future__ import annotations

from dataclasses import dataclass

from core.constants import MODEL_PRICING


@dataclass(frozen=True, slots=True)
class GenerationCostSnapshot:
    llm_cost_usd: float
    total_tokens_in: int
    total_tokens_out: int
    total_llm_calls: int


class GenerationCostTracker:
    """Accumulate LLM usage for the GENERATION phase."""

    def __init__(self) -> None:
        self.llm_cost_usd: float = 0.0
        self.total_tokens_in: int = 0
        self.total_tokens_out: int = 0
        self.total_llm_calls: int = 0

    def track_call(self, *, model: str, task: str, input_tokens: int, output_tokens: int) -> None:
        del task
        rates = MODEL_PRICING.get(model)
        if rates is None:
            return
        self.total_tokens_in += int(input_tokens)
        self.total_tokens_out += int(output_tokens)
        self.total_llm_calls += 1
        self.llm_cost_usd += (input_tokens / 1000.0) * rates["input"] + (output_tokens / 1000.0) * rates["output"]

    def snapshot(self) -> GenerationCostSnapshot:
        return GenerationCostSnapshot(
            llm_cost_usd=self.llm_cost_usd,
            total_tokens_in=self.total_tokens_in,
            total_tokens_out=self.total_tokens_out,
            total_llm_calls=self.total_llm_calls,
        )


def llm_delta_between_snapshots(
    before: GenerationCostSnapshot,
    after: GenerationCostSnapshot,
) -> tuple[int, int, float]:
    """Return (tokens_in, tokens_out, llm_cost_usd) added between two tracker snapshots."""
    return (
        after.total_tokens_in - before.total_tokens_in,
        after.total_tokens_out - before.total_tokens_out,
        after.llm_cost_usd - before.llm_cost_usd,
    )
```

#### `backend/modules/generation/diagram_generator.py`

**Language hint:** `python`

```python
"""Diagram generation: LLM -> PlantUML/Mermaid -> Kroki PNG."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Protocol

from core.constants import TASK_TO_MODEL
from core.exceptions import GenerationException
from infrastructure.sk_adapter import AzureSKAdapter
from modules.generation.context import build_prompt_mapping, evidence_text_from_retrieval
from modules.generation.cost_tracking import GenerationCostTracker, llm_delta_between_snapshots
from modules.generation.kroki import KrokiRenderer
from modules.generation.prompt_loader import GenerationPromptLoader
from modules.template.models import SectionDefinition

MAX_PLANTUML_ATTEMPTS = 3
MAX_MERMAID_ATTEMPTS = 2
MAX_DIAGRAM_CONTEXT_CHARS = 3500


class DiagramRenderClient(Protocol):
    async def render_png(self, diagram_type: str, source: str) -> bytes: ...


def _strip_code_fence(text: str) -> str:
    cleaned = text.strip()
    fence = re.search(
        r"^```(?:[a-zA-Z0-9_-]+)?\s*(.*?)\s*```$",
        cleaned,
        flags=re.DOTALL,
    )
    if fence:
        return fence.group(1).strip()
    return cleaned


def extract_plantuml(text: str) -> str:
    cleaned = _strip_code_fence(text)
    if "@startuml" in cleaned and "@enduml" in cleaned:
        start = cleaned.index("@startuml")
        end = cleaned.rindex("@enduml") + len("@enduml")
        return cleaned[start:end].strip()
    return cleaned.strip()


def extract_mermaid(text: str) -> str:
    return _strip_code_fence(text).strip()


class DiagramSectionGenerator:
    def __init__(
        self,
        sk_adapter: AzureSKAdapter,
        *,
        kroki: KrokiRenderer | DiagramRenderClient,
        storage_root: Path,
        prompt_loader: GenerationPromptLoader | None = None,
    ) -> None:
        self._sk = sk_adapter
        self._kroki = kroki
        self._storage_root = storage_root
        self._prompts = prompt_loader or GenerationPromptLoader()

    def is_configured(self) -> bool:
        if not self._sk.is_configured():
            return False
        if hasattr(self._kroki, "is_configured"):
            return bool(self._kroki.is_configured())
        return True

    def _write_png(self, workflow_run_id: str, section_id: str, fmt: str, attempt: int, data: bytes) -> str:
        rel_dir = Path("diagrams") / workflow_run_id
        out_dir = self._storage_root / rel_dir
        out_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{section_id}_{fmt}_a{attempt}.png"
        out_path = out_dir / filename
        out_path.write_bytes(data)
        return str(rel_dir / filename).replace("\\", "/")

    async def generate(
        self,
        *,
        workflow_run_id: str,
        section: SectionDefinition,
        retrieval_payload: dict[str, object] | None,
        doc_type: str,
        cost_tracker: GenerationCostTracker,
    ) -> dict[str, Any]:
        evidence_context = evidence_text_from_retrieval(
            retrieval_payload,
            max_chars=MAX_DIAGRAM_CONTEXT_CHARS,
        )
        base_mapping = build_prompt_mapping(section, doc_type, evidence_context)

        tokens_in = 0
        tokens_out = 0
        cost_usd = 0.0
        model = TASK_TO_MODEL["diagram_generation"]

        last_error: str | None = None
        diagram_path: str | None = None
        diagram_format: str | None = None
        last_source = ""

        plantuml_template = self._prompts.load_template("diagram", section.prompt_selector)
        correction_template = self._prompts.load_template("diagram", "correction")

        # Phase 1: PlantUML
        for attempt in range(1, MAX_PLANTUML_ATTEMPTS + 1):
            before = cost_tracker.snapshot()

            if attempt == 1:
                prompt = self._prompts.render_template(plantuml_template, base_mapping)
                prompt = self._tighten_diagram_prompt(prompt, kind="plantuml")
                try:
                    raw = await self._sk.invoke_text(
                        prompt,
                        task="diagram_generation",
                        cost_tracker=cost_tracker,
                    )
                except GenerationException as exc:
                    last_error = str(exc.message)
                    break
            else:
                correction_map = build_prompt_mapping(
                    section,
                    doc_type,
                    evidence_context,
                    render_error=last_error or "Unknown render error",
                    failed_diagram_source=last_source or "(empty)",
                )
                prompt = self._prompts.render_template(correction_template, correction_map)
                prompt = self._tighten_diagram_prompt(prompt, kind="plantuml")
                try:
                    raw = await self._sk.invoke_text(
                        prompt,
                        task="diagram_correction",
                        cost_tracker=cost_tracker,
                    )
                except GenerationException as exc:
                    last_error = str(exc.message)
                    break

            after = cost_tracker.snapshot()
            di, do, dc = llm_delta_between_snapshots(before, after)
            tokens_in += di
            tokens_out += do
            cost_usd += dc

            last_source = extract_plantuml(raw)
            if not last_source:
                last_error = "Generated PlantUML was empty."
                continue

            if "@startuml" not in last_source or "@enduml" not in last_source:
                last_error = "Generated PlantUML missing @startuml/@enduml."
                continue

            try:
                png = await self._kroki.render_png("plantuml", last_source)
            except GenerationException as exc:
                last_error = str(exc.message)
                continue

            diagram_path = self._write_png(workflow_run_id, section.section_id, "plantuml", attempt, png)
            diagram_format = "plantuml"

            return {
                "output_type": "diagram",
                "content": "",
                "diagram_path": diagram_path,
                "diagram_format": diagram_format,
                "diagram_source": last_source,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "cost_usd": cost_usd,
                "model": model,
                "task": "diagram_generation",
                "error": None,
            }

        # Phase 2: Mermaid fallback
        mermaid_template = self._prompts.load_template("diagram", "mermaid_default")
        for attempt in range(1, MAX_MERMAID_ATTEMPTS + 1):
            before = cost_tracker.snapshot()

            prompt = self._prompts.render_template(mermaid_template, base_mapping)
            prompt = self._tighten_diagram_prompt(prompt, kind="mermaid")
            try:
                raw = await self._sk.invoke_text(
                    prompt,
                    task="diagram_generation",
                    cost_tracker=cost_tracker,
                )
            except GenerationException as exc:
                last_error = str(exc.message)
                break

            after = cost_tracker.snapshot()
            di, do, dc = llm_delta_between_snapshots(before, after)
            tokens_in += di
            tokens_out += do
            cost_usd += dc

            source = extract_mermaid(raw)
            if not source:
                last_error = "Generated Mermaid source was empty."
                continue

            try:
                png = await self._kroki.render_png("mermaid", source)
            except GenerationException as exc:
                last_error = str(exc.message)
                continue

            diagram_path = self._write_png(workflow_run_id, section.section_id, "mermaid", attempt, png)
            diagram_format = "mermaid"

            return {
                "output_type": "diagram",
                "content": "",
                "diagram_path": diagram_path,
                "diagram_format": diagram_format,
                "diagram_source": source,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "cost_usd": cost_usd,
                "model": model,
                "task": "diagram_generation",
                "error": None,
            }

        # Phase 3: deterministic fallback diagram
        fallback_source = self._fallback_mermaid_source(section.title)
        try:
            png = await self._kroki.render_png("mermaid", fallback_source)
            diagram_path = self._write_png(workflow_run_id, section.section_id, "mermaid", 99, png)
            diagram_format = "mermaid"

            return {
                "output_type": "diagram",
                "content": "_Fallback diagram used because model generation failed._",
                "diagram_path": diagram_path,
                "diagram_format": diagram_format,
                "diagram_source": fallback_source,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "cost_usd": cost_usd,
                "model": model,
                "task": "diagram_generation",
                "error": None,
            }
        except GenerationException as exc:
            last_error = str(exc.message)

        err_text = last_error or "Diagram generation failed."
        return {
            "output_type": "diagram",
            "content": f"_Diagram generation failed: {err_text}_",
            "diagram_path": diagram_path,
            "diagram_format": diagram_format,
            "diagram_source": last_source,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cost_usd": cost_usd,
            "model": model,
            "task": "diagram_generation",
            "error": err_text,
        }

    def _tighten_diagram_prompt(self, prompt: str, *, kind: str) -> str:
        if kind == "plantuml":
            suffix = (
                "\n\nIMPORTANT:\n"
                "- Return ONLY raw PlantUML syntax.\n"
                "- Include @startuml and @enduml.\n"
                "- Do not include markdown fences.\n"
                "- Do not include explanations.\n"
                "- Keep the diagram compact and high-level.\n"
                "- Prefer at most 8 components/actors unless the evidence clearly requires more.\n"
            )
        else:
            suffix = (
                "\n\nIMPORTANT:\n"
                "- Return ONLY raw Mermaid syntax.\n"
                "- Do not include markdown fences.\n"
                "- Do not include explanations.\n"
                "- Keep the diagram compact and high-level.\n"
                "- Prefer at most 8 nodes/participants unless the evidence clearly requires more.\n"
            )
        return f"{prompt.rstrip()}{suffix}"

    def _fallback_mermaid_source(self, title: str) -> str:
        safe_title = (title or "Diagram").replace('"', "'").strip() or "Diagram"
        return (
            "flowchart TD\n"
            f' A["{safe_title}"] --> B["Details unavailable"]\n'
        )
```

#### `backend/modules/generation/kroki.py`

**Language hint:** `python`

```python
"""Kroki HTTP render client (PlantUML / Mermaid → PNG)."""

from __future__ import annotations

import httpx

from core.exceptions import GenerationException


class KrokiRenderer:
    def __init__(self, base_url: str, *, timeout_seconds: float = 60.0) -> None:
        self._base = base_url.rstrip("/")
        self._timeout = timeout_seconds

    def is_configured(self) -> bool:
        return bool(self._base)

    async def render_png(self, diagram_type: str, source: str) -> bytes:
        if not self.is_configured():
            raise GenerationException("Kroki URL is not configured.", code="KROKI_NOT_CONFIGURED")
        url = f"{self._base}/{diagram_type}/png"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    url,
                    content=source.encode("utf-8"),
                    headers={"Content-Type": "text/plain"},
                )
                response.raise_for_status()
                return response.content
        except httpx.HTTPError as exc:
            raise GenerationException(
                f"Kroki render failed for {diagram_type}: {exc}",
                code="KROKI_RENDER_FAILED",
            ) from exc
```

#### `backend/modules/generation/models.py`

**Language hint:** `python`

```python
"""Structured generation outputs persisted on ``WorkflowRecord.section_generation_results``."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class GenerationSectionResult(BaseModel):
    """One section row after GENERATION (matches docs/04 contract)."""

    model_config = ConfigDict(extra="ignore")

    output_type: str
    content: str = ""
    diagram_path: str | None = None
    diagram_format: str | None = None
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    model: str = ""
    task: str = ""
    error: str | None = None
    citations: list[dict[str, object]] = Field(default_factory=list)
```

#### `backend/modules/generation/observability.py`

**Language hint:** `python`

```python
"""Merge generation-phase observability into workflow summary."""

from __future__ import annotations

from typing import Any

from modules.observability.cost_rollup import merge_full_cost_summary


def merge_generation_observability(
    base: dict[str, Any] | None,
    *,
    llm_cost_usd: float,
    generated_sections: int,
    total_tokens_in: int = 0,
    total_tokens_out: int = 0,
    total_llm_calls: int = 0,
) -> dict[str, Any]:
    prior_in = int(base.get("total_tokens_in", 0) if isinstance(base, dict) else 0)
    prior_out = int(base.get("total_tokens_out", 0) if isinstance(base, dict) else 0)
    prior_calls = int(base.get("total_llm_calls", 0) if isinstance(base, dict) else 0)
    return merge_full_cost_summary(
        base,
        llm_cost_usd=llm_cost_usd,
        extra={
            "generated_sections": generated_sections,
            "total_tokens_in": prior_in + total_tokens_in,
            "total_tokens_out": prior_out + total_tokens_out,
            "total_llm_calls": prior_calls + total_llm_calls,
        },
    )
```

#### `backend/modules/generation/orchestrator.py`

**Language hint:** `python`

```python
"""Parallel, dependency-aware section generation orchestration."""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from time import perf_counter
from typing import Any

from core.exceptions import SDLCBaseException
from core.logging import get_logger
from modules.generation.context import citations_from_retrieval
from modules.generation.cost_tracking import GenerationCostTracker
from modules.generation.diagram_generator import DiagramSectionGenerator
from modules.generation.table_generator import TableSectionGenerator
from modules.generation.text_generator import TextSectionGenerator
from modules.template.models import SectionDefinition

logger = get_logger(__name__)

EmitFn = Callable[[str, str, dict[str, object] | None], Awaitable[None]]

DEFAULT_MAX_CONCURRENT_SECTIONS = 3


def compute_execution_waves(sections: list[SectionDefinition]) -> list[list[SectionDefinition]]:
    """Group sections into waves so dependencies run before dependents."""
    remaining: dict[str, SectionDefinition] = {s.section_id: s for s in sections}
    completed: set[str] = set()
    waves: list[list[SectionDefinition]] = []

    while remaining:
        wave = [
            s
            for s in remaining.values()
            if all(dep in completed for dep in (s.dependencies or []))
        ]

        if not wave:
            fallback = sorted(remaining.values(), key=lambda x: x.execution_order)[0]
            logger.warning(
                "generation.graph.stalled detail=dependency graph stalled "
                "section_id=%s remaining_ids=%s",
                fallback.section_id,
                sorted(remaining.keys()),
            )
            wave = [fallback]

        for s in wave:
            del remaining[s.section_id]

        waves.append(wave)
        completed.update(s.section_id for s in wave)

    return waves


class GenerationOrchestrator:
    def __init__(
        self,
        text_generator: TextSectionGenerator,
        table_generator: TableSectionGenerator,
        diagram_generator: DiagramSectionGenerator,
        *,
        max_concurrent_sections: int = DEFAULT_MAX_CONCURRENT_SECTIONS,
    ) -> None:
        self._text = text_generator
        self._table = table_generator
        self._diagram = diagram_generator
        self._max_concurrent = max(1, int(max_concurrent_sections))
        self._semaphore = asyncio.Semaphore(self._max_concurrent)

    def is_configured(self) -> bool:
        return (
            self._text.is_configured()
            and self._table.is_configured()
            and self._diagram.is_configured()
        )

    async def run_all_sections(
        self,
        *,
        workflow_run_id: str,
        sections: list[SectionDefinition],
        section_retrieval_results: dict[str, object],
        doc_type: str,
        cost_tracker: GenerationCostTracker,
        emit: EmitFn | None = None,
    ) -> dict[str, dict[str, Any]]:
        ordered = sorted(sections, key=lambda s: s.execution_order)
        waves = compute_execution_waves(ordered)

        logger.info(
            "generation.orchestrator.start workflow_run_id=%s "
            "total_sections=%s wave_count=%s max_concurrent=%s",
            workflow_run_id,
            len(ordered),
            len(waves),
            self._max_concurrent,
        )

        results: dict[str, dict[str, Any]] = {}

        for wave_index, wave in enumerate(waves, start=1):
            logger.info(
                "generation.wave.started workflow_run_id=%s wave_index=%s "
                "wave_size=%s section_ids=%s",
                workflow_run_id,
                wave_index,
                len(wave),
                [s.section_id for s in wave],
            )

            tasks: list[Awaitable[dict[str, Any]]] = []
            for section in wave:
                parent_title = self._find_parent_title(ordered, section.section_id)
                child_titles = self._collect_child_titles(ordered, section.section_id)

                tasks.append(
                    self._run_with_semaphore(
                        self._generate_one(
                            workflow_run_id=workflow_run_id,
                            section=section,
                            retrieval_payload=self._payload_for_section(
                                section_retrieval_results,
                                section.section_id,
                            ),
                            doc_type=doc_type,
                            cost_tracker=cost_tracker,
                            emit=emit,
                            parent_title=parent_title,
                            child_titles=child_titles,
                        )
                    )
                )

            outputs = await asyncio.gather(*tasks)

            for section, out in zip(wave, outputs):
                results[section.section_id] = out

            failures = sum(1 for out in outputs if out.get("error"))
            logger.info(
                "generation.wave.completed workflow_run_id=%s wave_index=%s "
                "completed=%s failed=%s",
                workflow_run_id,
                wave_index,
                len(outputs) - failures,
                failures,
            )

        logger.info(
            "generation.orchestrator.completed workflow_run_id=%s generated_sections=%s",
            workflow_run_id,
            len(results),
        )
        return results

    async def _run_with_semaphore(self, coro: Awaitable[dict[str, Any]]) -> dict[str, Any]:
        async with self._semaphore:
            return await coro

    @staticmethod
    def _payload_for_section(
        store: dict[str, object],
        section_id: str,
    ) -> dict[str, object] | None:
        raw = store.get(section_id)
        if isinstance(raw, dict):
            return dict(raw)
        return None

    @staticmethod
    def _find_parent_title(
        ordered_sections: list[SectionDefinition],
        section_id: str,
    ) -> str | None:
        current_index = next(
            (idx for idx, sec in enumerate(ordered_sections) if sec.section_id == section_id),
            None,
        )
        if current_index is None:
            return None

        current = ordered_sections[current_index]
        current_level = int(current.level)

        for idx in range(current_index - 1, -1, -1):
            candidate = ordered_sections[idx]
            if int(candidate.level) < current_level:
                return candidate.title

        return None

    @staticmethod
    def _collect_child_titles(
        ordered_sections: list[SectionDefinition],
        section_id: str,
    ) -> list[str]:
        current_index = next(
            (idx for idx, sec in enumerate(ordered_sections) if sec.section_id == section_id),
            None,
        )
        if current_index is None:
            return []

        current = ordered_sections[current_index]
        current_level = int(current.level)
        child_titles: list[str] = []

        for next_section in ordered_sections[current_index + 1:]:
            next_level = int(next_section.level)
            if next_level <= current_level:
                break
            child_titles.append(next_section.title)

        return child_titles

    async def _generate_one(
        self,
        *,
        workflow_run_id: str,
        section: SectionDefinition,
        retrieval_payload: dict[str, object] | None,
        doc_type: str,
        cost_tracker: GenerationCostTracker,
        emit: EmitFn | None,
        parent_title: str | None,
        child_titles: list[str],
    ) -> dict[str, Any]:
        citations = citations_from_retrieval(retrieval_payload)
        started_at = perf_counter()

        logger.info(
            "generation.section.started workflow_run_id=%s section_id=%s "
            "output_type=%s has_retrieval_payload=%s citation_count=%s "
            "parent_title=%s child_count=%s",
            workflow_run_id,
            section.section_id,
            section.output_type,
            retrieval_payload is not None,
            len(citations),
            parent_title,
            len(child_titles),
        )

        if emit:
            await emit(
                workflow_run_id,
                "section.generation.started",
                {
                    "section_id": section.section_id,
                    "output_type": section.output_type,
                },
            )

        try:
            if section.output_type == "text":
                result = await self._text.generate(
                    section=section,
                    retrieval_payload=retrieval_payload,
                    doc_type=doc_type,
                    cost_tracker=cost_tracker,
                    parent_title=parent_title,
                    child_titles=child_titles,
                )
            elif section.output_type == "table":
                result = await self._table.generate(
                    section=section,
                    retrieval_payload=retrieval_payload,
                    doc_type=doc_type,
                    cost_tracker=cost_tracker,
                )
            elif section.output_type == "diagram":
                result = await self._diagram.generate(
                    workflow_run_id=workflow_run_id,
                    section=section,
                    retrieval_payload=retrieval_payload,
                    doc_type=doc_type,
                    cost_tracker=cost_tracker,
                )
            else:
                result = {
                    "output_type": str(section.output_type),
                    "content": "",
                    "diagram_path": None,
                    "diagram_format": None,
                    "tokens_in": 0,
                    "tokens_out": 0,
                    "cost_usd": 0.0,
                    "model": "",
                    "task": "",
                    "error": f"Unsupported output_type: {section.output_type}",
                }

        except asyncio.CancelledError:
            raise
        except SDLCBaseException as exc:
            result = {
                "output_type": section.output_type,
                "content": "",
                "diagram_path": None,
                "diagram_format": None,
                "tokens_in": 0,
                "tokens_out": 0,
                "cost_usd": 0.0,
                "model": "",
                "task": "",
                "error": exc.message,
            }
        except Exception as exc:
            logger.exception(
                "generation.section.failed",
                extra={
                    "section_id": section.section_id,
                    "workflow_run_id": workflow_run_id,
                },
            )
            result = {
                "output_type": section.output_type,
                "content": "",
                "diagram_path": None,
                "diagram_format": None,
                "tokens_in": 0,
                "tokens_out": 0,
                "cost_usd": 0.0,
                "model": "",
                "task": "",
                "error": str(exc),
            }

        result["citations"] = citations
        duration_ms = int((perf_counter() - started_at) * 1000)

        logger.info(
            "generation.section.completed workflow_run_id=%s section_id=%s "
            "output_type=%s duration_ms=%s error=%s tokens_in=%s tokens_out=%s",
            workflow_run_id,
            section.section_id,
            result.get("output_type"),
            duration_ms,
            result.get("error"),
            result.get("tokens_in"),
            result.get("tokens_out"),
        )

        if emit:
            await emit(
                workflow_run_id,
                "section.generation.completed",
                {
                    "section_id": section.section_id,
                    "output_type": result.get("output_type"),
                    "error": result.get("error"),
                },
            )

        return result
```

#### `backend/modules/generation/prompt_loader.py`

**Language hint:** `python`

```python
"""Load plain-text generation prompts (YAML files read as UTF-8 templates)."""

from __future__ import annotations

from pathlib import Path

from core.exceptions import GenerationException


class GenerationPromptLoader:
    def __init__(self, prompts_root: Path | None = None) -> None:
        backend_root = Path(__file__).resolve().parents[2]
        self._root = prompts_root or (backend_root / "prompts" / "generation")

    @staticmethod
    def render_template(template: str, mapping: dict[str, str]) -> str:
        class _Missing(dict[str, str]):
            def __missing__(self, key: str) -> str:
                return ""

        return template.format_map(_Missing(mapping))

    def load_template(self, category: str, selector: str) -> str:
        """category: text | table | diagram"""
        normalized = self._normalize_selector(selector)
        path = self._root / category / f"{normalized}.yaml"
        if not path.is_file():
            path = self._root / category / "default.yaml"
        if not path.is_file():
            raise GenerationException(f"Missing generation prompt for {category}/{selector}", code="PROMPT_MISSING")
        return path.read_text(encoding="utf-8")

    @staticmethod
    def _normalize_selector(selector: str) -> str:
        cleaned = (selector or "default").strip().lower().replace(" ", "_")
        return cleaned or "default"
```

#### `backend/modules/generation/table_generator.py`

**Language hint:** `python`

```python
"""LLM markdown table generation."""
from __future__ import annotations

import re
from typing import Any

from core.constants import TASK_TO_MODEL
from infrastructure.sk_adapter import AzureSKAdapter
from modules.generation.context import build_prompt_mapping, evidence_text_from_retrieval
from modules.generation.cost_tracking import GenerationCostTracker, llm_delta_between_snapshots
from modules.generation.prompt_loader import GenerationPromptLoader
from modules.template.models import SectionDefinition


_TABLE_LINE_RE = re.compile(r"^\s*\|.+\|\s*$")
_SEPARATOR_CELL_RE = re.compile(r"^\s*:?-{3,}:?\s*$")


def _unwrap_table_line(line: str) -> str:
    """
    Remove decorative wrappers that sometimes surround model output lines,
    for example **_| a | b |_**.
    """
    stripped = line.strip()

    wrappers = [
        ("**_", "_**"),
        ("**", "**"),
        ("__", "__"),
        ("_", "_"),
    ]
    for prefix, suffix in wrappers:
        if stripped.startswith(prefix) and stripped.endswith(suffix) and len(stripped) > len(prefix) + len(suffix):
            inner = stripped[len(prefix):-len(suffix)].strip()
            if "|" in inner:
                return inner
    return stripped


def _split_pipe_cells(line: str) -> list[str]:
    body = line.strip().strip("|")
    return [cell.strip() for cell in body.split("|")]


def _is_separator_row(line: str) -> bool:
    cells = _split_pipe_cells(_unwrap_table_line(line))
    if not cells:
        return False
    return all(_SEPARATOR_CELL_RE.match(cell) is not None for cell in cells)


def _extract_first_table_lines(text: str) -> list[str]:
    """
    Return the first contiguous pipe-table block found in the model output.
    """
    lines = text.splitlines()
    table_lines: list[str] = []
    collecting = False

    for raw in lines:
        line = _unwrap_table_line(raw)
        if _TABLE_LINE_RE.match(line):
            table_lines.append(line)
            collecting = True
            continue

        if collecting:
            break

    return table_lines


def _normalize_markdown_table(text: str) -> str:
    """
    Normalize the first detected markdown pipe table into a clean GFM table:
    - header row
    - separator row
    - normalized pipe formatting

    If no table block is found, return the original stripped text.
    """
    table_lines = _extract_first_table_lines(text)
    if len(table_lines) < 2:
        return text.strip()

    header_cells = _split_pipe_cells(table_lines[0])
    if not header_cells:
        return text.strip()

    body_lines = table_lines[1:]

    normalized: list[str] = []
    normalized.append("| " + " | ".join(header_cells) + " |")

    if body_lines and _is_separator_row(body_lines[0]):
        normalized.append("| " + " | ".join("---" for _ in header_cells) + " |")
        data_lines = body_lines[1:]
    else:
        normalized.append("| " + " | ".join("---" for _ in header_cells) + " |")
        data_lines = body_lines

    for line in data_lines:
        clean = _unwrap_table_line(line)
        if not _TABLE_LINE_RE.match(clean):
            continue
        normalized.append("| " + " | ".join(_split_pipe_cells(clean)) + " |")

    return "\n".join(normalized).strip()


class TableSectionGenerator:
    def __init__(self, sk_adapter: AzureSKAdapter, prompt_loader: GenerationPromptLoader | None = None) -> None:
        self._sk = sk_adapter
        self._prompts = prompt_loader or GenerationPromptLoader()

    def is_configured(self) -> bool:
        return self._sk.is_configured()

    def _task_for_section(self, section: SectionDefinition) -> str:
        if section.is_complex:
            return "complex_section"
        return "table_generation"

    async def generate(
        self,
        *,
        section: SectionDefinition,
        retrieval_payload: dict[str, object] | None,
        doc_type: str,
        cost_tracker: GenerationCostTracker,
    ) -> dict[str, Any]:
        template = self._prompts.load_template("table", section.prompt_selector)
        evidence_context = evidence_text_from_retrieval(retrieval_payload)
        mapping = build_prompt_mapping(section, doc_type, evidence_context)
        prompt = self._prompts.render_template(template, mapping)

        task = self._task_for_section(section)
        model = TASK_TO_MODEL[task]

        before = cost_tracker.snapshot()
        raw_text = await self._sk.invoke_text(prompt, task=task, cost_tracker=cost_tracker)
        after = cost_tracker.snapshot()

        t_in, t_out, cost_usd = llm_delta_between_snapshots(before, after)
        normalized_table = _normalize_markdown_table(raw_text.strip())

        return {
            "output_type": "table",
            "content": normalized_table,
            "diagram_path": None,
            "diagram_format": None,
            "tokens_in": t_in,
            "tokens_out": t_out,
            "cost_usd": cost_usd,
            "model": model,
            "task": task,
            "error": None,
        }
```

#### `backend/modules/generation/text_generator.py`

**Language hint:** `python`

```python
"""LLM text section generation."""
from __future__ import annotations

import re
import unicodedata
from typing import Any

from core.constants import TASK_TO_MODEL
from infrastructure.sk_adapter import AzureSKAdapter
from modules.generation.context import build_prompt_mapping, evidence_text_from_retrieval
from modules.generation.cost_tracking import GenerationCostTracker, llm_delta_between_snapshots
from modules.generation.prompt_loader import GenerationPromptLoader
from modules.template.models import SectionDefinition


_META_LEADIN_RE = re.compile(
    r"^(this section|this document|the following section|the following)\b.*"
    r"\b(defines|describes|captures|records|outlines|summarizes|documents|provides)\b",
    flags=re.IGNORECASE,
)

_DECORATIVE_WRAPPER_PATTERNS = (
    re.compile(r"^\s*\*\*_(.+?)_\*\*\s*$"),
    re.compile(r"^\s*__\*(.+?)\*__\s*$"),
    re.compile(r"^\s*\*\*(.+?)\*\*\s*$"),
)


def _normalize_paragraph_key(value: str) -> str:
    text = unicodedata.normalize("NFKC", value or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _split_paragraphs(text: str) -> list[str]:
    if not text.strip():
        return []
    return [part.strip() for part in re.split(r"\n\s*\n", text.strip()) if part.strip()]


def _dedupe_paragraphs(text: str) -> str:
    paragraphs = _split_paragraphs(text)
    seen: set[str] = set()
    kept: list[str] = []

    for para in paragraphs:
        key = _normalize_paragraph_key(para)
        if not key:
            continue
        if key in seen:
            continue
        seen.add(key)
        kept.append(para)

    return "\n\n".join(kept).strip()


def _remove_generic_parent_leadin(text: str, *, has_children: bool) -> str:
    """
    For parent sections, drop the first paragraph if it is a generic
    'This section provides/defines/describes ...' lead-in.
    """
    if not has_children:
        return text.strip()

    paragraphs = _split_paragraphs(text)
    if not paragraphs:
        return ""

    cleaned: list[str] = []
    for idx, para in enumerate(paragraphs):
        if idx == 0 and _META_LEADIN_RE.match(para):
            continue
        cleaned.append(para)

    return "\n\n".join(cleaned).strip()


def _strip_decorative_emphasis(text: str) -> str:
    """
    Remove full-line decorative wrappers like **_..._**, **...**, etc.,
    while preserving the inner text.
    """
    cleaned_lines: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        replaced = False
        for pattern in _DECORATIVE_WRAPPER_PATTERNS:
            match = pattern.match(stripped)
            if match:
                cleaned_lines.append(match.group(1).strip())
                replaced = True
                break
        if not replaced:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def _tighten_parent_bullets(text: str, *, has_children: bool) -> str:
    """
    Parent sections should stay compact. If a parent section contains too many
    bullets, keep the first few to avoid re-writing child-section detail.
    """
    if not has_children:
        return text.strip()

    lines = text.splitlines()
    bullet_indices: list[int] = []
    bullet_re = re.compile(r"^\s*[-*•]\s+.+$")
    for idx, line in enumerate(lines):
        if bullet_re.match(line.strip()):
            bullet_indices.append(idx)

    if len(bullet_indices) <= 6:
        return text.strip()

    keep_indices = set(bullet_indices[:6])
    trimmed_lines: list[str] = []
    for idx, line in enumerate(lines):
        if idx in bullet_indices and idx not in keep_indices:
            continue
        trimmed_lines.append(line)

    return "\n".join(trimmed_lines).strip()


def _postprocess_text_output(
    text: str,
    *,
    child_titles: list[str] | None,
) -> str:
    cleaned = (text or "").strip()
    cleaned = _strip_decorative_emphasis(cleaned)
    cleaned = _remove_generic_parent_leadin(
        cleaned,
        has_children=bool(child_titles),
    )
    cleaned = _tighten_parent_bullets(
        cleaned,
        has_children=bool(child_titles),
    )
    cleaned = _dedupe_paragraphs(cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned


class TextSectionGenerator:
    def __init__(self, sk_adapter: AzureSKAdapter, prompt_loader: GenerationPromptLoader | None = None) -> None:
        self._sk = sk_adapter
        self._prompts = prompt_loader or GenerationPromptLoader()

    def is_configured(self) -> bool:
        return self._sk.is_configured()

    def _task_for_section(self, section: SectionDefinition) -> str:
        if section.is_complex:
            return "complex_section"
        return "text_generation"

    async def generate(
        self,
        *,
        section: SectionDefinition,
        retrieval_payload: dict[str, object] | None,
        doc_type: str,
        cost_tracker: GenerationCostTracker,
        parent_title: str | None = None,
        child_titles: list[str] | None = None,
    ) -> dict[str, Any]:
        template = self._prompts.load_template("text", section.prompt_selector)
        evidence_context = evidence_text_from_retrieval(retrieval_payload)
        mapping = build_prompt_mapping(
            section,
            doc_type,
            evidence_context,
            parent_section_title=parent_title or "",
            child_section_titles=child_titles or [],
        )
        prompt = self._prompts.render_template(template, mapping)

        task = self._task_for_section(section)
        model = TASK_TO_MODEL[task]

        before = cost_tracker.snapshot()
        raw_text = await self._sk.invoke_text(prompt, task=task, cost_tracker=cost_tracker)
        after = cost_tracker.snapshot()

        t_in, t_out, cost_usd = llm_delta_between_snapshots(before, after)
        final_text = _postprocess_text_output(
            raw_text.strip(),
            child_titles=child_titles,
        )

        return {
            "output_type": "text",
            "content": final_text,
            "diagram_path": None,
            "diagram_format": None,
            "tokens_in": t_in,
            "tokens_out": t_out,
            "cost_usd": cost_usd,
            "model": model,
            "task": task,
            "error": None,
        }
```

#### `backend/modules/ingestion/__init__.py`

**Language hint:** `python`

```python
"""BRD ingestion: parse, chunk, index (once per document)."""

from modules.ingestion.chunker import DocumentChunker, IngestionChunk
from modules.ingestion.indexer import DocumentIndexer
from modules.ingestion.ingestion_coordinator import IngestionCoordinator, IngestionRunResult
from modules.ingestion.orchestrator import IngestionOrchestrator
from modules.ingestion.parser import DocumentParser

__all__ = [
    "DocumentChunker",
    "DocumentIndexer",
    "DocumentParser",
    "IngestionChunk",
    "IngestionCoordinator",
    "IngestionOrchestrator",
    "IngestionRunResult",
]
```

#### `backend/modules/ingestion/chunker.py`

**Language hint:** `python`

```python
"""Hybrid chunking for parsed BRD documents."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from core.ids import chunk_id_for_document
from core.token_count import count_tokens
from infrastructure.doc_intelligence import ParsedDocument

_HEADING_RE = re.compile(
    r"(?m)^(#{1,6}\s+.+|[A-Z][A-Z0-9\s\-]{4,}|(?:\d+(?:\.\d+)*)\s+[^\n]+)\s*$",
)
_TOKEN_RE = re.compile(r"\S+")


@dataclass(slots=True, frozen=True)
class IngestionChunk:
    chunk_id: str
    document_id: str
    workflow_run_id: str
    text: str
    chunk_index: int
    section_heading: str | None
    page_number: int | None
    content_type: str


class DocumentChunker:
    """Split parsed content into table and text chunks."""

    def __init__(
        self,
        *,
        chunk_size: int = 512,
        overlap: int = 64,
        token_mode: str = "tiktoken",
    ) -> None:
        self._chunk_size = max(32, chunk_size)
        self._overlap = max(0, min(overlap, self._chunk_size - 1))
        normalized_mode = (token_mode or "tiktoken").strip().lower()
        self._token_mode = normalized_mode if normalized_mode in {"tiktoken", "word"} else "tiktoken"

    def chunk(
        self,
        *,
        document_id: str,
        workflow_run_id: str,
        parsed: ParsedDocument,
    ) -> list[IngestionChunk]:
        chunks: list[IngestionChunk] = []
        chunk_index = 0
        page_markers = self._page_markers(parsed.raw_result)

        for table in parsed.tables:
            text = table.markdown.strip()
            if not text:
                continue
            chunks.append(
                IngestionChunk(
                    chunk_id=chunk_id_for_document(document_id, chunk_index),
                    document_id=document_id,
                    workflow_run_id=workflow_run_id,
                    text=text,
                    chunk_index=chunk_index,
                    section_heading="Table",
                    page_number=table.page_number,
                    content_type="table",
                ),
            )
            chunk_index += 1

        for heading, body, start_offset in self._split_sections(parsed.full_text):
            page_number = self._resolve_page_from_offset(start_offset, page_markers)
            for text_piece in self._sliding_windows(body):
                if self._token_count(text_piece) < 10:
                    continue
                chunks.append(
                    IngestionChunk(
                        chunk_id=chunk_id_for_document(document_id, chunk_index),
                        document_id=document_id,
                        workflow_run_id=workflow_run_id,
                        text=text_piece,
                        chunk_index=chunk_index,
                        section_heading=heading,
                        page_number=page_number,
                        content_type="text",
                    ),
                )
                chunk_index += 1

        return chunks

    def _split_sections(self, text: str) -> list[tuple[str | None, str, int]]:
        original = text
        text = text.strip()
        if not text:
            return []

        matches = list(_HEADING_RE.finditer(text))
        if not matches:
            return [(None, text, max(0, original.find(text)))]

        sections: list[tuple[str | None, str, int]] = []
        cursor = 0
        for index, match in enumerate(matches):
            heading = match.group(0).strip()
            start = match.end()
            if match.start() > cursor:
                preface = text[cursor : match.start()].strip()
                if preface:
                    sections.append((None, preface, max(0, original.find(preface))))
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            if body:
                sections.append((heading, body, max(0, original.find(body))))
            cursor = end
        if not sections:
            sections.append((None, text, max(0, original.find(text))))
        return sections

    def _sliding_windows(self, text: str) -> list[str]:
        if self._token_mode == "word" or self._encoding() is None:
            return self._sliding_windows_word_fallback(text)

        token_ids = self._encode_tokens(text)
        if not token_ids:
            return []
        if len(token_ids) <= self._chunk_size:
            single = self._decode_tokens(token_ids).strip()
            return [single] if single else []

        out: list[str] = []
        step = max(1, self._chunk_size - self._overlap)
        for start in range(0, len(token_ids), step):
            window = token_ids[start : start + self._chunk_size]
            if not window:
                break
            text_window = self._decode_tokens(window).strip()
            if text_window:
                out.append(text_window)
            if start + self._chunk_size >= len(token_ids):
                break
        return out

    def _sliding_windows_word_fallback(self, text: str) -> list[str]:
        tokens = _TOKEN_RE.findall(text)
        if not tokens:
            return []
        if len(tokens) <= self._chunk_size:
            return [" ".join(tokens)]

        out: list[str] = []
        step = max(1, self._chunk_size - self._overlap)
        for start in range(0, len(tokens), step):
            window = tokens[start : start + self._chunk_size]
            if not window:
                break
            out.append(" ".join(window))
            if start + self._chunk_size >= len(tokens):
                break
        return out

    def _token_count(self, text: str) -> int:
        return count_tokens(text)

    def _encode_tokens(self, text: str) -> list[int]:
        encoding = self._encoding()
        if encoding is None:
            return []
        try:
            return encoding.encode(text)
        except Exception:
            return []

    def _decode_tokens(self, token_ids: list[int]) -> str:
        encoding = self._encoding()
        if encoding is None:
            return ""
        try:
            return encoding.decode(token_ids)
        except Exception:
            return ""

    @staticmethod
    @lru_cache(maxsize=1)
    def _encoding():
        try:
            import tiktoken  # type: ignore

            return tiktoken.get_encoding("cl100k_base")
        except Exception:
            return None

    def _page_markers(self, raw_result: dict[str, Any]) -> list[tuple[int, int]]:
        markers: list[tuple[int, int]] = []
        paragraphs = raw_result.get("paragraphs") if isinstance(raw_result, dict) else None
        if not isinstance(paragraphs, list):
            return markers

        for paragraph in paragraphs:
            if not isinstance(paragraph, dict):
                continue
            spans = paragraph.get("spans")
            regions = paragraph.get("boundingRegions")
            if not isinstance(spans, list) or not spans:
                continue
            if not isinstance(regions, list) or not regions:
                continue
            first_span = spans[0]
            first_region = regions[0]
            if not isinstance(first_span, dict) or not isinstance(first_region, dict):
                continue
            offset = first_span.get("offset")
            page = first_region.get("pageNumber")
            if isinstance(offset, int) and isinstance(page, int):
                markers.append((offset, page))

        markers.sort(key=lambda item: item[0])
        return markers

    def _resolve_page_from_offset(self, offset: int, markers: list[tuple[int, int]]) -> int | None:
        if not markers:
            return None
        page: int | None = None
        for marker_offset, marker_page in markers:
            if marker_offset <= offset:
                page = marker_page
            else:
                break
        return page if page is not None else markers[0][1]
```

#### `backend/modules/ingestion/indexer.py`

**Language hint:** `python`

```python
"""Embed and upsert chunks into Azure AI Search."""

from __future__ import annotations

from modules.ingestion.chunker import IngestionChunk
from core.constants import MODEL_PRICING
from infrastructure.search_client import AzureSearchClient, SearchChunk
from infrastructure.sk_adapter import AzureSKAdapter


class DocumentIndexer:
    """Generate embeddings and upsert chunks in batches."""

    def __init__(
        self,
        search_client: AzureSearchClient,
        sk_adapter: AzureSKAdapter,
        *,
        batch_size: int = 50,
    ) -> None:
        self._search_client = search_client
        self._sk_adapter = sk_adapter
        self._batch_size = max(1, batch_size)

    def is_configured(self) -> bool:
        return self._search_client.is_configured() and self._sk_adapter.is_configured()

    async def index_chunks(self, chunks: list[IngestionChunk]) -> tuple[int, float]:
        if not chunks:
            return 0, 0.0

        with_vectors: list[SearchChunk] = []
        input_tokens = 0
        for chunk in chunks:
            embedding_result = await self._sk_adapter.generate_embedding_with_usage(chunk.text)
            input_tokens += embedding_result.prompt_tokens
            with_vectors.append(
                SearchChunk(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    workflow_run_id=chunk.workflow_run_id,
                    text=chunk.text,
                    chunk_index=chunk.chunk_index,
                    section_heading=chunk.section_heading,
                    page_number=chunk.page_number,
                    content_type=chunk.content_type,
                    embedding=embedding_result.embedding,
                ),
            )

        indexed = 0
        for start in range(0, len(with_vectors), self._batch_size):
            batch = with_vectors[start : start + self._batch_size]
            indexed += await self._search_client.upsert_chunks(batch)

        rate = MODEL_PRICING["text-embedding-3-large"]["input"]
        embedding_cost = (input_tokens / 1000.0) * rate
        return indexed, embedding_cost
```

#### `backend/modules/ingestion/ingestion_coordinator.py`

**Language hint:** `python`

```python
"""Serialize ingest per BRD and skip Phase 2 when chunks already indexed (ingest-once)."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from core.constants import DocumentIngestionStatus
from core.ids import utc_now_iso

if TYPE_CHECKING:
    from repositories.document_models import DocumentRecord
    from repositories.document_repo import DocumentRepository


@dataclass(frozen=True, slots=True)
class IngestionRunResult:
    """Result when ingestion actually runs (not skipped)."""

    chunk_count: int
    page_count: int | None
    language: str | None
    embedding_cost_usd: float
    document_intelligence_cost_usd: float


class IngestionCoordinator:
    """Per-process asyncio lock per document_id + persisted INDEXED flag.

    Policy:
    - Chunks in Azure AI Search are keyed by stable ``chunk_id`` (see ``chunk_id_for_document``).
    - Only one ingest pipeline runs at a time for a given ``document_id`` (concurrent workflows wait).
    - If ``DocumentRecord.ingestion_status == INDEXED``, Phase 2 is skipped (PDD+SDD+UAT reuse the same index).
    - Re-running after FAILED is allowed; upserts remain idempotent.
    """

    def __init__(self, document_repo: DocumentRepository) -> None:
        self._document_repo = document_repo
        self._locks: dict[str, asyncio.Lock] = {}

    def _lock(self, document_id: str) -> asyncio.Lock:
        if document_id not in self._locks:
            self._locks[document_id] = asyncio.Lock()
        return self._locks[document_id]

    async def run_ingestion_if_needed(
        self,
        document_id: str,
        ingest: Callable[[DocumentRecord], Awaitable[IngestionRunResult]],
    ) -> tuple[bool, IngestionRunResult | None]:
        """Return ``(skipped, result)`` where ``skipped`` means Phase 2 did not run."""
        async with self._lock(document_id):
            doc = self._document_repo.get_or_raise(document_id)
            if doc.ingestion_status == DocumentIngestionStatus.INDEXED:
                return True, None

            try:
                result = await ingest(doc)
            except Exception as exc:  # noqa: BLE001 — surface to workflow layer
                self._document_repo.update(
                    document_id,
                    ingestion_status=DocumentIngestionStatus.FAILED,
                    last_ingestion_error=str(exc),
                )
                raise

            self._document_repo.update(
                document_id,
                ingestion_status=DocumentIngestionStatus.INDEXED,
                indexed_chunk_count=result.chunk_count,
                indexed_at=utc_now_iso(),
                last_ingestion_error=None,
                page_count=result.page_count if result.page_count is not None else doc.page_count,
                language=result.language if result.language is not None else doc.language,
            )
            return False, result
```

#### `backend/modules/ingestion/orchestrator.py`

**Language hint:** `python`

```python
"""Parse -> chunk -> index ingestion pipeline."""

from __future__ import annotations

from pathlib import Path

from modules.ingestion.chunker import DocumentChunker
from modules.ingestion.indexer import DocumentIndexer
from modules.ingestion.ingestion_coordinator import IngestionRunResult
from modules.ingestion.parser import DocumentParser
from modules.observability.cost_rollup import document_intelligence_cost_usd
from services.event_service import EventService


class IngestionOrchestrator:
    def __init__(
        self,
        parser: DocumentParser,
        chunker: DocumentChunker,
        indexer: DocumentIndexer,
        event_service: EventService,
    ) -> None:
        self._parser = parser
        self._chunker = chunker
        self._indexer = indexer
        self._event_service = event_service

    def is_configured(self) -> bool:
        return self._parser.is_configured() and self._indexer.is_configured()

    async def run(
        self,
        *,
        workflow_run_id: str,
        document_id: str,
        file_path: Path,
        content_type: str,
    ) -> IngestionRunResult:
        parsed = await self._parser.parse(file_path, content_type=content_type)
        await self._event_service.emit(
            workflow_run_id,
            "ingestion.parse.completed",
            {"pages": parsed.page_count, "language": parsed.language},
        )

        chunks = self._chunker.chunk(
            document_id=document_id,
            workflow_run_id=workflow_run_id,
            parsed=parsed,
        )
        await self._event_service.emit(
            workflow_run_id,
            "ingestion.chunk.completed",
            {"chunk_count": len(chunks)},
        )

        indexed_count, embedding_cost = await self._indexer.index_chunks(chunks)
        await self._event_service.emit(
            workflow_run_id,
            "ingestion.index.completed",
            {"indexed_count": indexed_count, "embedding_cost_usd": embedding_cost},
        )

        return IngestionRunResult(
            chunk_count=indexed_count,
            page_count=parsed.page_count,
            language=parsed.language,
            embedding_cost_usd=embedding_cost,
            document_intelligence_cost_usd=document_intelligence_cost_usd(parsed.page_count),
        )
```

#### `backend/modules/ingestion/parser.py`

**Language hint:** `python`

```python
"""Document parsing wrapper for ingestion."""
from __future__ import annotations

from mimetypes import guess_type
from pathlib import Path

from core.exceptions import IngestionException
from infrastructure.doc_intelligence import AzureDocIntelligenceClient, ParsedDocument


def _normalize_content_type(file_path: Path, content_type: str | None) -> str:
    """
    Normalize content type before sending bytes to Azure Document Intelligence.

    Why:
    - Upstream callers may pass generic content types like application/octet-stream.
    - For Office/PDF files, it's safer to send an explicit MIME type when possible.
    """
    raw = (content_type or "").strip().lower()

    # Keep non-generic explicit content types as-is
    if raw and raw not in {"application/octet-stream", "binary/octet-stream"}:
        return raw

    # Try Python's mimetype inference first
    guessed, _ = guess_type(str(file_path))
    if guessed:
        return guessed

    # Strong fallback by extension
    suffix = file_path.suffix.lower()
    if suffix == ".docx":
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if suffix == ".xlsx":
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    if suffix == ".pptx":
        return "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    if suffix == ".pdf":
        return "application/pdf"

    return "application/octet-stream"


class DocumentParser:
    """Load a document from disk and parse with Azure Document Intelligence."""

    def __init__(self, doc_client: AzureDocIntelligenceClient) -> None:
        self._doc_client = doc_client

    def is_configured(self) -> bool:
        return self._doc_client.is_configured()

    async def parse(self, file_path: Path, *, content_type: str) -> ParsedDocument:
        if not file_path.exists():
            raise IngestionException(f"Document file not found: {file_path}")

        payload = file_path.read_bytes()
        if not payload:
            raise IngestionException(f"Document file is empty: {file_path}")

        normalized_content_type = _normalize_content_type(file_path, content_type)

        return await self._doc_client.analyze_document(
            payload,
            content_type=normalized_content_type,
        )
```

#### `backend/modules/observability/__init__.py`

**Language hint:** `python`

```python
"""Cost rollup and observability helpers."""
```

#### `backend/modules/observability/cost_rollup.py`

**Language hint:** `python`

```python
"""Roll LLM, embedding, and Document Intelligence estimates into one observability summary."""

from __future__ import annotations

from typing import Any

from core.config import settings
from core.constants import MODEL_PRICING


def llm_call_cost_usd(*, model_key: str, tokens_in: int, tokens_out: int) -> float:
    rates = MODEL_PRICING[model_key]
    return (tokens_in / 1000.0) * rates["input"] + (tokens_out / 1000.0) * rates["output"]


def document_intelligence_cost_usd(page_count: int) -> float:
    return max(0, page_count) * settings.document_intelligence_usd_per_page


def merge_full_cost_summary(
    base: dict[str, Any] | None,
    *,
    llm_cost_usd: float = 0.0,
    embedding_cost_usd: float = 0.0,
    document_intelligence_cost_usd: float = 0.0,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build/extend ``observability_summary`` with full dollar estimates.

    WorkflowExecutor should pass cumulative costs as phases complete. Non-LLM lines use
    ``document_intelligence_usd`` and ``embedding_cost_usd`` explicitly so the UI can
    show a single ``total_cost_usd`` that matches invoices (within model accuracy).
    """
    out: dict[str, Any] = dict(base or {})
    out["llm_cost_usd"] = float(out.get("llm_cost_usd", 0.0)) + llm_cost_usd
    out["embedding_cost_usd"] = float(out.get("embedding_cost_usd", 0.0)) + embedding_cost_usd
    out["document_intelligence_cost_usd"] = float(
        out.get("document_intelligence_cost_usd", 0.0),
    ) + document_intelligence_cost_usd
    out["total_cost_usd"] = (
        out["llm_cost_usd"] + out["embedding_cost_usd"] + out["document_intelligence_cost_usd"]
    )
    if extra:
        out.update(extra)
    return out
```

#### `backend/modules/retrieval/__init__.py`

**Language hint:** `python`

```python
"""Retrieval module exports."""

from modules.retrieval.packager import Citation, EvidenceBundle, EvidencePackager
from modules.retrieval.retriever import RetrievedChunk, SectionRetriever, merge_retrieval_observability

__all__ = [
    "Citation",
    "EvidenceBundle",
    "EvidencePackager",
    "RetrievedChunk",
    "SectionRetriever",
    "merge_retrieval_observability",
]
```

#### `backend/modules/retrieval/packager.py`

**Language hint:** `python`

```python
"""Evidence packaging for section-level retrieval results."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Citation(BaseModel):
    model_config = ConfigDict(extra="ignore")

    path: str
    page: int | None = None
    content_type: str = "text"
    chunk_id: str


class EvidenceBundle(BaseModel):
    model_config = ConfigDict(extra="ignore")

    section_id: str
    context_text: str = ""
    citations: list[Citation] = Field(default_factory=list)


class EvidencePackager:
    """Convert retrieved chunks into generator-ready evidence bundles."""

    def package(self, section_id: str, chunks: list[object]) -> EvidenceBundle:
        citations: list[Citation] = []
        source_blocks: list[str] = []

        for index, chunk in enumerate(chunks, start=1):
            chunk_id = str(getattr(chunk, "chunk_id", "") or "")
            text = str(getattr(chunk, "text", "") or "")
            path = str(getattr(chunk, "section_heading", "") or "Document")
            page = self._to_optional_int(getattr(chunk, "page_number", None))
            content_type = str(getattr(chunk, "content_type", "") or "text")

            citations.append(
                Citation(
                    path=path,
                    page=page,
                    content_type=content_type,
                    chunk_id=chunk_id,
                ),
            )

            page_label = f"p.{page}" if page is not None else "p.?"
            source_blocks.append(
                f"[Source {index} - {path}, {page_label} ({content_type})]\n{text}",
            )

        context_text = "\n\n---\n\n".join(source_blocks)
        return EvidenceBundle(section_id=section_id, context_text=context_text, citations=citations)

    @staticmethod
    def _to_optional_int(value: object) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
```

#### `backend/modules/retrieval/retriever.py`

**Language hint:** `python`

```python
"""Section-level adaptive retrieval over Azure AI Search."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from time import perf_counter


from core.config import settings
from core.constants import MODEL_PRICING
from infrastructure.search_client import AzureSearchClient
from infrastructure.sk_adapter import AzureSKAdapter
from modules.template.models import SectionDefinition
from modules.observability.cost_rollup import merge_full_cost_summary

MIN_DIRECT_QUERY_WORDS = 4
logger = logging.getLogger(__name__)

@dataclass(slots=True)
class RetrievedChunk:
    chunk_id: str
    text: str
    section_heading: str | None
    page_number: int | None
    content_type: str
    score: float = 0.0


class SectionRetriever:
    """Resolve section query, search chunks, and return normalized retrieval hits."""

    def __init__(
        self,
        search_client: AzureSearchClient,
        sk_adapter: AzureSKAdapter,
        *,
        top_k: int | None = None,
    ) -> None:
        self._search_client = search_client
        self._sk_adapter = sk_adapter
        self._top_k = top_k if top_k is not None else settings.retrieval_top_k

    def is_configured(self) -> bool:
        return self._search_client.is_configured() and self._sk_adapter.is_configured()

    async def retrieve_for_section(
        self,
        section: SectionDefinition,
        *,
        document_id: str,
        cost_tracker: object | None = None,
    ) -> tuple[list[RetrievedChunk], float]:
        started_at = perf_counter()

        query_text = await self._resolve_query(section, cost_tracker=cost_tracker)
        embedding_result = await self._sk_adapter.generate_embedding_with_usage(query_text)

        raw = await self._search_client.hybrid_search(
            search_text=query_text,
            embedding=embedding_result.embedding,
            document_id=document_id,
            top_k=self._top_k,
        )

        rate = MODEL_PRICING["text-embedding-3-large"]["input"]
        embedding_cost_usd = (embedding_result.prompt_tokens / 1000.0) * rate

        chunks: list[RetrievedChunk] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            chunks.append(
                RetrievedChunk(
                    chunk_id=str(item.get("chunk_id") or ""),
                    text=str(item.get("text") or ""),
                    section_heading=self._as_optional_str(item.get("section_heading")),
                    page_number=self._as_optional_int(item.get("page_number")),
                    content_type=str(item.get("content_type") or "text"),
                    score=float(item.get("@search.score") or item.get("score") or 0.0),
                ),
            )

        duration_ms = int((perf_counter() - started_at) * 1000)
        logger.info(
            "retrieval.section.metrics section_id=%s document_id=%s top_k=%s query_word_count=%s "
            "chunk_count=%s embedding_cost_usd=%s duration_ms=%s",
            section.section_id,
            document_id,
            self._top_k,
            len(query_text.split()),
            len(chunks),
            embedding_cost_usd,
            duration_ms,
        )

        return chunks, embedding_cost_usd

    async def _resolve_query(
        self,
        section: SectionDefinition,
        *,
        cost_tracker: object | None = None,
    ) -> str:
        direct_query = (section.retrieval_query or "").strip()
        if len(direct_query.split()) >= MIN_DIRECT_QUERY_WORDS:
            return direct_query

        prompt = self._build_query_generation_prompt(section)
        generated = (
            await self._sk_adapter.invoke_text(
                prompt,
                task="retrieval_query_generation",
                cost_tracker=cost_tracker,
            )
        ).strip()
        if len(generated.split()) >= MIN_DIRECT_QUERY_WORDS:
            return generated
        if direct_query:
            return direct_query
        return f"{section.title} {section.description}".strip()

    @staticmethod
    def _build_query_generation_prompt(section: SectionDefinition) -> str:
        return (
            "Generate one concise enterprise-search query (8-12 words) for retrieving source evidence.\n"
            "Return plain text only.\n\n"
            f"Section title: {section.title}\n"
            f"Section description: {section.description}\n"
            f"Section hints: {section.generation_hints}\n"
            f"Current retrieval query: {section.retrieval_query}\n"
        )

    @staticmethod
    def _as_optional_int(value: object) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _as_optional_str(value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None


def merge_retrieval_observability(
    base: dict[str, object] | None,
    *,
    llm_cost_usd: float = 0.0,
    embedding_cost_usd: float,
    retrieved_sections: int,
    total_tokens_in: int = 0,
    total_tokens_out: int = 0,
    total_llm_calls: int = 0,
) -> dict[str, object]:
    return merge_full_cost_summary(
        base,
        llm_cost_usd=llm_cost_usd,
        embedding_cost_usd=embedding_cost_usd,
        extra={
            "retrieved_sections": retrieved_sections,
            "total_tokens_in": int(base.get("total_tokens_in", 0) if isinstance(base, dict) else 0) + total_tokens_in,
            "total_tokens_out": int(base.get("total_tokens_out", 0) if isinstance(base, dict) else 0)
            + total_tokens_out,
            "total_llm_calls": int(base.get("total_llm_calls", 0) if isinstance(base, dict) else 0) + total_llm_calls,
        },
    )
```

#### `backend/modules/template/__init__.py`

**Language hint:** `python`

```python
"""Template module package."""

from modules.template.models import (
    DocumentSkeleton,
    PageSetup,
    ParagraphStyle,
    SectionDefinition,
    StyleMap,
    TableStyle,
)

__all__ = [
    "DocumentSkeleton",
    "PageSetup",
    "ParagraphStyle",
    "SectionDefinition",
    "StyleMap",
    "TableStyle",
]
```

#### `backend/modules/template/classifier.py`

**Language hint:** `python`

```python
"""Section classification for custom template headings."""

from __future__ import annotations

from pathlib import Path
from string import Template
from typing import Any

import yaml

from core.exceptions import TemplateException
from core.logging import get_logger
from infrastructure.sk_adapter import AzureSKAdapter
from modules.template.models import DocumentSkeleton, ExtractedHeading

logger = get_logger(__name__)


class TemplateClassifier:
    def __init__(self, sk_adapter: AzureSKAdapter, prompt_path: Path | None = None) -> None:
        self._sk_adapter = sk_adapter
        base = Path(__file__).resolve().parents[2]
        self._prompt_candidates: list[Path] = [
            prompt_path if prompt_path is not None else base / "prompts" / "template" / "classifier.yaml",
            base / "prompts" / "template" / "classifier.yaml",
            base / "prompts" / "classifier.yaml",
        ]

    def is_configured(self) -> bool:
        return self._sk_adapter.is_configured()

    async def classify_sections(self, skeleton: DocumentSkeleton) -> list[dict[str, Any]]:
        """
        Classify extracted headings into structured section metadata.

        Fallback behavior:
        - If SK adapter is not configured -> heuristic fallback
        - If prompt file is missing -> heuristic fallback
        - If model returns invalid/empty JSON -> heuristic fallback
        """
        heading_items = self._resolve_heading_items(skeleton)
        if not heading_items:
            return []

        if not self.is_configured():
            logger.info("template.classifier.fallback reason=adapter_not_configured")
            return self._fallback_all(heading_items)

        try:
            prompt_template = self._load_prompt_template()
        except TemplateException:
            logger.warning("template.classifier.fallback reason=prompt_missing")
            return self._fallback_all(heading_items)

        headings_blob = "\n".join(self._format_heading_line(item) for item in heading_items)

        prompt = Template(prompt_template).safe_substitute(
            headings=headings_blob,
            title=skeleton.title or "",
        )

        try:
            payload = await self._sk_adapter.invoke_json(prompt, task="template_classification")
        except Exception:
            logger.exception("template.classifier.invoke_json.failed")
            return self._fallback_all(heading_items)

        if not isinstance(payload, dict):
            logger.warning("template.classifier.fallback reason=payload_not_dict")
            return self._fallback_all(heading_items)

        raw_items = payload.get("sections")
        if not isinstance(raw_items, list):
            logger.warning("template.classifier.fallback reason=sections_missing_or_invalid")
            return self._fallback_all(heading_items)

        results: list[dict[str, Any]] = []

        for idx, item in enumerate(raw_items):
            if not isinstance(item, dict):
                continue

            fallback_heading = (
                heading_items[min(idx, len(heading_items) - 1)].text
                if heading_items
                else f"Section {idx + 1}"
            )

            required_fields = item.get("required_fields") or []
            if not isinstance(required_fields, list):
                required_fields = []

            results.append(
                {
                    "heading": str(item.get("heading") or fallback_heading),
                    "output_type": self._normalize_output_type(str(item.get("output_type") or "text")),
                    "description": str(item.get("description") or ""),
                    "prompt_selector": str(item.get("prompt_selector") or "default"),
                    "required_fields": [str(field) for field in required_fields],
                    "is_complex": bool(item.get("is_complex") or False),
                }
            )

        if not results:
            logger.warning("template.classifier.fallback reason=empty_results")
            return self._fallback_all(heading_items)

        # Ensure one result per heading, preserving order
        if len(results) < len(heading_items):
            for idx in range(len(results), len(heading_items)):
                results.append(self._fallback_classification(idx, heading_items[idx].text))

        if len(results) > len(heading_items):
            results = results[: len(heading_items)]

        logger.info("template.classifier.completed sections=%s", len(results))
        return results

    def _resolve_heading_items(self, skeleton: DocumentSkeleton) -> list[ExtractedHeading]:
        if skeleton.heading_items:
            return list(skeleton.heading_items)

        return [
            ExtractedHeading(
                text=heading,
                level=1,
                order=index + 1,
                style_name=None,
                numbering=None,
            )
            for index, heading in enumerate(skeleton.headings)
        ]

    def _format_heading_line(self, item: ExtractedHeading) -> str:
        numbering = f"{item.numbering} " if item.numbering else ""
        return f'- [L{item.level}] {numbering}{item.text}'

    def _load_prompt_template(self) -> str:
        """
        Search for the classifier prompt in multiple supported locations.

        Supported formats:
        - YAML:
            prompt: |
              ...
        - Plain text prompt file
        """
        checked: list[str] = []

        for candidate in self._prompt_candidates:
            if candidate is None:
                continue

            checked.append(str(candidate))
            if not candidate.is_file():
                continue

            raw = candidate.read_text(encoding="utf-8")

            try:
                data = yaml.safe_load(raw)
            except Exception:
                data = None

            if isinstance(data, dict):
                for key in ("prompt", "template", "content", "text"):
                    value = data.get(key)
                    if isinstance(value, str) and value.strip():
                        logger.info("template.classifier.prompt.loaded path=%s", str(candidate))
                        return value

            if raw.strip():
                logger.info("template.classifier.prompt.loaded path=%s", str(candidate))
                return raw

        raise TemplateException(
            f"Template classifier prompt missing. Checked: {', '.join(checked)}"
        )

    def _fallback_all(self, heading_items: list[ExtractedHeading]) -> list[dict[str, Any]]:
        return [
            self._fallback_classification(index, item.text)
            for index, item in enumerate(heading_items)
        ]

    def _fallback_classification(self, index: int, heading: str) -> dict[str, Any]:
        lower = heading.lower()
        output_type = "text"

        if any(token in lower for token in ("matrix", "table", "register", "log", "grid", "checklist")):
            output_type = "table"

        if any(token in lower for token in ("diagram", "architecture", "flow", "sequence", "component")):
            output_type = "diagram"

        return {
            "heading": heading,
            "output_type": output_type,
            "description": f"Generated section for heading: {heading}",
            "prompt_selector": "default",
            "required_fields": [],
            "is_complex": index <= 1,
        }

    def _normalize_output_type(self, value: str) -> str:
        normalized = value.strip().lower()
        if normalized in {"text", "table", "diagram"}:
            return normalized
        return "text"
```

#### `backend/modules/template/extractor.py`

**Language hint:** `python`

```python
"""Template skeleton and style extraction for custom templates."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

from core.exceptions import TemplateException
from modules.template.models import DocumentSkeleton, ExtractedHeading, StyleMap

_WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
_SHEET_NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


class TemplateExtractor:
    # TOC title lines
    _TOC_TITLE_RE = re.compile(r"^(table of contents|contents)$", re.IGNORECASE)

    # TOC entry examples:
    # 1 Introduction ............ 3
    # 2.1 Scope ............ 5
    # Appendix A ............ 10
    _TOC_LINE_RE = re.compile(r"^(?:\d+(?:\.\d+)*)?\s*.+?\.{2,}\s*\d+\s*$")

    # Numbered body headings:
    # 1 Introduction
    # 2.1 Scope
    _NUMBERED_HEADING_RE = re.compile(r"^(?P<num>\d+(?:\.\d+)*)\s+\S+")
    _HEADING_STYLE_LEVEL_RE = re.compile(r"heading\s*(\d+)$", re.IGNORECASE)

    def extract(self, template_path: Path) -> tuple[DocumentSkeleton, StyleMap, dict[str, object]]:
        suffix = template_path.suffix.lower()
        if suffix == ".docx":
            return self.extract_docx(template_path)
        if suffix == ".xlsx":
            return self.extract_xlsx(template_path)
        raise TemplateException(f"Unsupported template format: {template_path.suffix}")

    def extract_docx(self, template_path: Path) -> tuple[DocumentSkeleton, StyleMap, dict[str, object]]:
        heading_items: list[ExtractedHeading] = []

        with ZipFile(template_path, "r") as archive:
            try:
                document_xml = archive.read("word/document.xml")
            except KeyError as exc:
                raise TemplateException("Invalid DOCX template: missing word/document.xml") from exc

        root = ET.fromstring(document_xml)

        in_toc = False
        saw_toc = False
        order = 0
        previous_key: tuple[str, int] | None = None

        for paragraph in root.findall(".//w:p", _WORD_NS):
            text = "".join(node.text or "" for node in paragraph.findall(".//w:t", _WORD_NS)).strip()
            if not text:
                continue

            style_name_node = paragraph.find(".//w:pStyle", _WORD_NS)
            style_value = ""
            if style_name_node is not None:
                style_value = (
                    style_name_node.attrib.get(f'{{{_WORD_NS["w"]}}}val') or ""
                ).strip().lower()

            normalized_text = self._normalize_text(text)

            # Start TOC detection
            if self._is_toc_title(normalized_text):
                in_toc = True
                saw_toc = True
                continue

            if self._is_toc_style(style_value):
                in_toc = True
                saw_toc = True
                continue

            # Skip TOC content until the first real heading after TOC
            if in_toc:
                if self._looks_like_toc_line(normalized_text):
                    continue

                if not self._is_real_heading(normalized_text, style_value):
                    continue

                # First real heading after TOC
                in_toc = False

            if not self._is_real_heading(normalized_text, style_value):
                continue

            level = self._derive_heading_level(normalized_text, style_value)
            numbering = self._extract_numbering_prefix(normalized_text)

            # Only dedupe exact repeated adjacent heading text/level pairs
            key = (normalized_text.lower(), level)
            if previous_key == key:
                continue
            previous_key = key

            order += 1
            heading_items.append(
                ExtractedHeading(
                    text=normalized_text,
                    level=level,
                    order=order,
                    style_name=style_value or None,
                    numbering=numbering,
                ),
            )

        if not heading_items:
            raise TemplateException("No headings detected in DOCX template for compilation.")

        headings = [item.text for item in heading_items]

        skeleton = DocumentSkeleton(
            title=template_path.stem,
            headings=headings,
            heading_items=heading_items,
            raw_structure={
                "source": "docx",
                "heading_count": len(heading_items),
                "toc_detected": saw_toc,
                "levels": [item.level for item in heading_items],
            },
        )
        return skeleton, StyleMap(), {}

    def extract_xlsx(self, template_path: Path) -> tuple[DocumentSkeleton, StyleMap, dict[str, object]]:
        with ZipFile(template_path, "r") as archive:
            try:
                workbook_xml = archive.read("xl/workbook.xml")
            except KeyError as exc:
                raise TemplateException("Invalid XLSX template: missing xl/workbook.xml") from exc

        root = ET.fromstring(workbook_xml)
        sheet_names: list[str] = []
        heading_items: list[ExtractedHeading] = []

        for sheet in root.findall(".//s:sheets/s:sheet", _SHEET_NS):
            name = sheet.attrib.get("name")
            if name:
                sheet_names.append(name.strip())

        if not sheet_names:
            raise TemplateException("No worksheets detected in XLSX template for compilation.")

        for idx, name in enumerate(sheet_names, start=1):
            heading_items.append(
                ExtractedHeading(
                    text=name,
                    level=1,
                    order=idx,
                    style_name="worksheet",
                    numbering=None,
                ),
            )

        skeleton = DocumentSkeleton(
            title=template_path.stem,
            headings=sheet_names,
            heading_items=heading_items,
            raw_structure={
                "source": "xlsx",
                "sheet_count": len(sheet_names),
            },
        )
        sheet_map = {
            "sheets": [{"name": name, "index": i + 1} for i, name in enumerate(sheet_names)],
        }
        return skeleton, StyleMap(), sheet_map

    def _normalize_text(self, text: str) -> str:
        return " ".join((text or "").split()).strip()

    def _is_toc_title(self, text: str) -> bool:
        return bool(self._TOC_TITLE_RE.match(text))

    def _is_toc_style(self, style_value: str) -> bool:
        if not style_value:
            return False
        return style_value.startswith("toc")

    def _looks_like_toc_line(self, text: str) -> bool:
        return bool(self._TOC_LINE_RE.match(text))

    def _is_real_heading(self, text: str, style_value: str) -> bool:
        """
        Detect actual body headings while excluding TOC content.
        """
        if not text:
            return False

        if self._is_toc_style(style_value):
            return False

        if self._looks_like_toc_line(text):
            return False

        is_heading = "heading" in style_value

        if not is_heading and self._NUMBERED_HEADING_RE.match(text):
            is_heading = True

        if not is_heading and text.isupper() and len(text.split()) <= 12:
            is_heading = True

        return is_heading

    def _derive_heading_level(self, text: str, style_value: str) -> int:
        """
        Prefer explicit Heading N styles. Otherwise infer from numbering depth.
        """
        if style_value:
            style_match = self._HEADING_STYLE_LEVEL_RE.search(style_value)
            if style_match:
                try:
                    return max(1, int(style_match.group(1)))
                except ValueError:
                    pass

        numbering = self._extract_numbering_prefix(text)
        if numbering:
            return numbering.count(".") + 1

        return 1

    def _extract_numbering_prefix(self, text: str) -> str | None:
        match = self._NUMBERED_HEADING_RE.match(text)
        if not match:
            return None
        return match.group("num")
```

#### `backend/modules/template/inbuilt/__init__.py`

**Language hint:** `python`

```python
"""Inbuilt template definitions."""
```

#### `backend/modules/template/inbuilt/pdd_sections.py`

**Language hint:** `python`

```python
"""Inbuilt PDD section definitions."""

from __future__ import annotations

from modules.template.models import SectionDefinition


PDD_SECTIONS: list[SectionDefinition] = [
    SectionDefinition(
        section_id="sec-pdd-overview",
        title="Project Overview",
        description="Describe the business context and expected outcomes.",
        execution_order=1,
        prompt_selector="overview",
        retrieval_query="project overview business goals scope",
    ),
    SectionDefinition(
        section_id="sec-pdd-scope",
        title="Scope",
        description="In-scope and out-of-scope boundaries.",
        execution_order=2,
        prompt_selector="scope",
        retrieval_query="scope boundaries in scope out of scope",
    ),
    SectionDefinition(
        section_id="sec-pdd-stakeholders",
        title="Stakeholder Matrix",
        description="Primary stakeholders and their responsibilities.",
        execution_order=3,
        output_type="table",
        prompt_selector="stakeholders",
        required_fields=["stakeholder", "role", "responsibility"],
        table_headers=["Stakeholder", "Role", "Responsibility"],
    ),
    SectionDefinition(
        section_id="sec-pdd-requirements",
        title="Functional Requirements",
        description="Prioritized business requirements.",
        execution_order=4,
        prompt_selector="requirements",
        retrieval_query="functional requirements business rules acceptance criteria",
        is_complex=True,
    ),
    SectionDefinition(
        section_id="sec-pdd-assumptions",
        title="Assumptions and Constraints",
        description="Constraints, assumptions, and dependencies.",
        execution_order=5,
        prompt_selector="assumptions",
    ),
    SectionDefinition(
        section_id="sec-pdd-risks",
        title="Risk Register",
        description="Known risks and proposed mitigations.",
        execution_order=6,
        output_type="table",
        prompt_selector="risk_register",
        table_headers=["Risk", "Impact", "Likelihood", "Mitigation"],
    ),
    SectionDefinition(
        section_id="sec-pdd-traceability",
        title="Traceability Matrix",
        description="Mapping of objectives to requirements and tests.",
        execution_order=7,
        output_type="table",
        prompt_selector="traceability_matrix",
        table_headers=["Objective", "Requirement", "Validation"],
    ),
    SectionDefinition(
        section_id="sec-pdd-summary",
        title="Executive Summary",
        description="Concise summary and implementation recommendation.",
        execution_order=8,
        prompt_selector="overview",
        dependencies=["sec-pdd-requirements", "sec-pdd-risks"],
    ),
]
```

#### `backend/modules/template/inbuilt/registry.py`

**Language hint:** `python`

```python
"""Registry for inbuilt section plans and style maps."""

from __future__ import annotations

from copy import deepcopy

from core.constants import DocType, INBUILT_TEMPLATE_ID_BY_DOC_TYPE
from modules.template.inbuilt.pdd_sections import PDD_SECTIONS
from modules.template.inbuilt.sdd_sections import SDD_SECTIONS
from modules.template.inbuilt.styles.pdd_style import PDD_STYLE_MAP
from modules.template.inbuilt.styles.sdd_style import SDD_STYLE_MAP
from modules.template.inbuilt.styles.uat_style import UAT_STYLE_MAP
from modules.template.inbuilt.uat_sections import UAT_SECTIONS
from modules.template.models import SectionDefinition, StyleMap


_SECTION_REGISTRY: dict[DocType, list[SectionDefinition]] = {
    DocType.PDD: PDD_SECTIONS,
    DocType.SDD: SDD_SECTIONS,
    DocType.UAT: UAT_SECTIONS,
}

_STYLE_REGISTRY: dict[DocType, StyleMap] = {
    DocType.PDD: PDD_STYLE_MAP,
    DocType.SDD: SDD_STYLE_MAP,
    DocType.UAT: UAT_STYLE_MAP,
}


def get_inbuilt_section_plan(doc_type: str | DocType) -> list[SectionDefinition]:
    resolved = DocType(doc_type)
    # Return deep copies so callers can safely mutate without side effects.
    return [SectionDefinition.model_validate(item.model_dump()) for item in deepcopy(_SECTION_REGISTRY[resolved])]


def get_inbuilt_style_map(doc_type: str | DocType) -> StyleMap:
    resolved = DocType(doc_type)
    return StyleMap.model_validate(deepcopy(_STYLE_REGISTRY[resolved].model_dump()))


def is_inbuilt_template_id(template_id: str) -> bool:
    return template_id in set(INBUILT_TEMPLATE_ID_BY_DOC_TYPE.values())


def doc_type_for_inbuilt_template(template_id: str) -> DocType:
    for doc_type, inbuilt_id in INBUILT_TEMPLATE_ID_BY_DOC_TYPE.items():
        if inbuilt_id == template_id:
            return doc_type
    raise ValueError(f"Unknown inbuilt template id: {template_id}")
```

#### `backend/modules/template/inbuilt/sdd_sections.py`

**Language hint:** `python`

```python
"""Inbuilt SDD section definitions."""

from __future__ import annotations

from modules.template.models import SectionDefinition


SDD_SECTIONS: list[SectionDefinition] = [
    SectionDefinition(
        section_id="sec-sdd-architecture-overview",
        title="Architecture Overview",
        description="High-level architecture summary.",
        execution_order=1,
        prompt_selector="architecture",
        is_complex=True,
    ),
    SectionDefinition(
        section_id="sec-sdd-architecture-diagram",
        title="System Architecture Diagram",
        description="Visual representation of major components and flows.",
        execution_order=2,
        output_type="diagram",
        prompt_selector="architecture",
        dependencies=["sec-sdd-architecture-overview"],
    ),
    SectionDefinition(
        section_id="sec-sdd-components",
        title="Component Design",
        description="Detailed component-level behavior and interfaces.",
        execution_order=3,
        prompt_selector="requirements",
        is_complex=True,
    ),
    SectionDefinition(
        section_id="sec-sdd-apis",
        title="API Specification",
        description="Core service contracts and payload expectations.",
        execution_order=4,
        output_type="table",
        prompt_selector="api_specification",
        table_headers=["API", "Method", "Request", "Response"],
    ),
    SectionDefinition(
        section_id="sec-sdd-security",
        title="Security Considerations",
        description="Security controls, data handling, and compliance notes.",
        execution_order=5,
        prompt_selector="risks",
    ),
    SectionDefinition(
        section_id="sec-sdd-deployment",
        title="Deployment and Operations",
        description="Deployment topology and runtime operations.",
        execution_order=6,
        prompt_selector="overview",
    ),
]
```

#### `backend/modules/template/inbuilt/styles/__init__.py`

**Language hint:** `python`

```python
"""Inbuilt template style maps."""
```

#### `backend/modules/template/inbuilt/styles/pdd_style.py`

**Language hint:** `python`

```python
"""Inbuilt style map for PDD."""

from __future__ import annotations

from modules.template.models import PageSetup, ParagraphStyle, StyleMap, TableStyle


PDD_STYLE_MAP = StyleMap(
    heading_1=ParagraphStyle(font_name="Calibri", font_size_pt=16, bold=True),
    heading_2=ParagraphStyle(font_name="Calibri", font_size_pt=13, bold=True),
    body=ParagraphStyle(font_name="Calibri", font_size_pt=11),
    table=TableStyle(header_fill="#0f172a", header_text_color="#ffffff", border_color="#cbd5e1"),
    page_setup=PageSetup(orientation="portrait"),
)
```

#### `backend/modules/template/inbuilt/styles/sdd_style.py`

**Language hint:** `python`

```python
"""Inbuilt style map for SDD."""

from __future__ import annotations

from modules.template.models import PageSetup, ParagraphStyle, StyleMap, TableStyle


SDD_STYLE_MAP = StyleMap(
    heading_1=ParagraphStyle(font_name="Calibri", font_size_pt=16, bold=True),
    heading_2=ParagraphStyle(font_name="Calibri", font_size_pt=13, bold=True),
    body=ParagraphStyle(font_name="Calibri", font_size_pt=11),
    table=TableStyle(header_fill="#1d4ed8", header_text_color="#ffffff", border_color="#93c5fd"),
    page_setup=PageSetup(orientation="portrait"),
)
```

#### `backend/modules/template/inbuilt/styles/uat_style.py`

**Language hint:** `python`

```python
"""Inbuilt style map for UAT."""

from __future__ import annotations

from modules.template.models import PageSetup, ParagraphStyle, StyleMap, TableStyle


UAT_STYLE_MAP = StyleMap(
    heading_1=ParagraphStyle(font_name="Calibri", font_size_pt=15, bold=True),
    heading_2=ParagraphStyle(font_name="Calibri", font_size_pt=12, bold=True),
    body=ParagraphStyle(font_name="Calibri", font_size_pt=10),
    table=TableStyle(header_fill="#065f46", header_text_color="#ffffff", border_color="#6ee7b7"),
    page_setup=PageSetup(orientation="landscape"),
)
```

#### `backend/modules/template/inbuilt/uat_sections.py`

**Language hint:** `python`

```python
"""Inbuilt UAT section definitions."""

from __future__ import annotations

from modules.template.models import SectionDefinition


UAT_SECTIONS: list[SectionDefinition] = [
    SectionDefinition(
        section_id="sec-uat-summary",
        title="Test Summary",
        description="Summary of UAT goals, test scope, and assumptions.",
        execution_order=1,
        prompt_selector="overview",
    ),
    SectionDefinition(
        section_id="sec-uat-test-cases",
        title="Test Cases",
        description="UAT test case definitions and expected outcomes.",
        execution_order=2,
        output_type="table",
        prompt_selector="default",
        table_headers=["ID", "Scenario", "Steps", "Expected Result"],
    ),
    SectionDefinition(
        section_id="sec-uat-defects",
        title="Defect Log",
        description="Known defects captured during UAT.",
        execution_order=3,
        output_type="table",
        prompt_selector="risk_register",
        table_headers=["Defect", "Severity", "Status", "Owner"],
    ),
    SectionDefinition(
        section_id="sec-uat-signoff",
        title="Sign-Off",
        description="Final approval details and release recommendation.",
        execution_order=4,
        prompt_selector="overview",
        dependencies=["sec-uat-test-cases", "sec-uat-defects"],
    ),
]
```

#### `backend/modules/template/models.py`

**Language hint:** `python`

```python
"""Shared template models for inbuilt and custom pipelines."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ParagraphStyle(BaseModel):
    model_config = ConfigDict(extra="ignore")

    font_name: str = "Calibri"
    font_size_pt: int = 11
    bold: bool = False
    italic: bool = False
    alignment: str = "left"


class TableStyle(BaseModel):
    model_config = ConfigDict(extra="ignore")

    header_fill: str = "#1f2937"
    header_text_color: str = "#ffffff"
    border_color: str = "#d1d5db"
    row_striping: bool = True


class PageSetup(BaseModel):
    model_config = ConfigDict(extra="ignore")

    orientation: Literal["portrait", "landscape"] = "portrait"
    margin_top_in: float = 1.0
    margin_right_in: float = 1.0
    margin_bottom_in: float = 1.0
    margin_left_in: float = 1.0


class StyleMap(BaseModel):
    model_config = ConfigDict(extra="ignore")

    heading_1: ParagraphStyle = Field(
        default_factory=lambda: ParagraphStyle(font_size_pt=16, bold=True),
    )
    heading_2: ParagraphStyle = Field(
        default_factory=lambda: ParagraphStyle(font_size_pt=13, bold=True),
    )
    body: ParagraphStyle = Field(default_factory=ParagraphStyle)
    table: TableStyle = Field(default_factory=TableStyle)
    page_setup: PageSetup = Field(default_factory=PageSetup)


class ExtractedHeading(BaseModel):
    """
    Structured heading extracted from a custom template.

    - text: normalized heading text
    - level: hierarchy level (1 = section, 2 = subsection, ...)
    - order: appearance order in source document
    - style_name: original style identifier when available
    - numbering: numbering prefix like '1', '1.2', '3.4.5' when detected
    """

    model_config = ConfigDict(extra="ignore")

    text: str
    level: int = 1
    order: int
    style_name: str | None = None
    numbering: str | None = None


class DocumentSkeleton(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str

    # Backward-compatible flat list
    headings: list[str] = Field(default_factory=list)

    # Preferred structured representation for custom templates
    heading_items: list[ExtractedHeading] = Field(default_factory=list)

    table_headers_by_heading: dict[str, list[str]] = Field(default_factory=dict)
    raw_structure: dict[str, object] = Field(default_factory=dict)


class SectionDefinition(BaseModel):
    model_config = ConfigDict(extra="ignore")

    section_id: str
    title: str
    description: str = ""
    execution_order: int

    output_type: Literal["text", "table", "diagram"] = "text"
    prompt_selector: str = "default"

    retrieval_query: str = ""
    generation_hints: str = ""
    expected_length: str = "medium"
    tone: str = "professional"

    level: int = 1
    parent_section_id: str | None = None

    dependencies: list[str] = Field(default_factory=list)
    required_fields: list[str] = Field(default_factory=list)
    table_headers: list[str] = Field(default_factory=list)
    is_complex: bool = False
```

#### `backend/modules/template/planner.py`

**Language hint:** `python`

```python
"""Build a normalized section plan for custom templates."""

from __future__ import annotations

import re
from typing import Any

from modules.template.models import DocumentSkeleton, ExtractedHeading, SectionDefinition


class SectionPlanner:
    def build_from_skeleton_and_classifications(
        self,
        skeleton: DocumentSkeleton,
        classifications: list[dict[str, Any]],
    ) -> list[SectionDefinition]:
        heading_items = self._resolve_heading_items(skeleton)
        plan: list[SectionDefinition] = []

        # Maintain most recent section_id seen at each level
        parent_stack: dict[int, str] = {}

        for index, heading_item in enumerate(heading_items):
            details = self._classification_for_index(classifications, index)

            output_type = str(details.get("output_type") or "text")
            normalized_output_type = (
                "table"
                if output_type == "table"
                else "diagram"
                if output_type == "diagram"
                else "text"
            )

            level = max(1, int(heading_item.level))
            parent_section_id = self._resolve_parent_section_id(parent_stack, level)

            section = SectionDefinition(
                section_id=self._make_section_id(index, heading_item.text),
                title=heading_item.text,
                description=str(details.get("description") or ""),
                execution_order=index + 1,
                output_type=normalized_output_type,
                prompt_selector=str(details.get("prompt_selector") or "default"),
                retrieval_query=self._default_retrieval_query(heading_item.text),
                generation_hints=str(details.get("generation_hints") or ""),
                required_fields=[str(v) for v in (details.get("required_fields") or [])],
                table_headers=skeleton.table_headers_by_heading.get(heading_item.text, []),
                is_complex=bool(details.get("is_complex") or False),
                level=level,
                parent_section_id=parent_section_id,
            )

            # Reset deeper levels when a new heading arrives at this level
            self._update_parent_stack(parent_stack, level, section.section_id)
            plan.append(section)

        return plan

    def _resolve_heading_items(self, skeleton: DocumentSkeleton) -> list[ExtractedHeading]:
        if skeleton.heading_items:
            return list(skeleton.heading_items)

        # Backward-compatible fallback if old skeletons exist
        return [
            ExtractedHeading(
                text=heading,
                level=1,
                order=index + 1,
                style_name=None,
                numbering=None,
            )
            for index, heading in enumerate(skeleton.headings)
        ]

    def _classification_for_index(self, classifications: list[dict[str, Any]], index: int) -> dict[str, Any]:
        if 0 <= index < len(classifications):
            item = classifications[index]
            if isinstance(item, dict):
                return item
        return {}

    def _resolve_parent_section_id(self, parent_stack: dict[int, str], level: int) -> str | None:
        if level <= 1:
            return None

        for candidate_level in range(level - 1, 0, -1):
            parent_id = parent_stack.get(candidate_level)
            if parent_id:
                return parent_id

        return None

    def _update_parent_stack(self, parent_stack: dict[int, str], level: int, section_id: str) -> None:
        # Remove deeper levels when entering a new branch
        stale_levels = [lvl for lvl in parent_stack.keys() if lvl >= level]
        for lvl in stale_levels:
            parent_stack.pop(lvl, None)

        parent_stack[level] = section_id

    def _make_section_id(self, index: int, heading: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")
        if not slug:
            slug = f"section-{index + 1}"
        return f"sec-custom-{index + 1}-{slug[:40]}"

    def _default_retrieval_query(self, heading: str) -> str:
        return f"{heading} requirements constraints dependencies"
```

#### `backend/modules/template/preview_generator.py`

**Language hint:** `python`

```python
"""Generate preview assets for compiled custom templates."""

from __future__ import annotations

from html import escape
from pathlib import Path
from zipfile import ZipFile

from core.exceptions import TemplateException
from modules.template.models import DocumentSkeleton, SectionDefinition


class TemplatePreviewGenerator:
    def build_preview_docx(
        self,
        *,
        destination: Path,
        title: str,
        section_plan: list[SectionDefinition],
    ) -> Path:
        lines = [f"Template Preview: {title}", ""]

        for section in section_plan:
            indent = "  " * max(0, section.level - 1)
            lines.append(f"{indent}{section.execution_order}. {section.title}")
            lines.append(f"{indent}Generated content placeholder.")
            lines.append("")

        destination.parent.mkdir(parents=True, exist_ok=True)
        self._write_minimal_docx(destination, lines)
        return destination

    def build_preview_html_from_xlsx(self, skeleton: DocumentSkeleton) -> str:
        if not skeleton.headings:
            raise TemplateException("Cannot build XLSX preview without sheet headings.")

        rows = "".join(
            f"<tr><td>{index + 1}</td><td>{escape(name)}</td></tr>"
            for index, name in enumerate(skeleton.headings)
        )
        return (
            "<div><h3>Template Preview</h3>"
            "<table><thead><tr><th>#</th><th>Sheet</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></div>"
        )

    def _write_minimal_docx(self, destination: Path, lines: list[str]) -> None:
        paragraph_xml = "".join(
            f"<w:p><w:r><w:t>{self._escape_xml(line)}</w:t></w:r></w:p>"
            for line in lines
        )
        document_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            f"<w:body>{paragraph_xml}</w:body>"
            "</w:document>"
        )
        content_types = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            "</Types>"
        )
        rels = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
            'Target="word/document.xml"/>'
            "</Relationships>"
        )

        with ZipFile(destination, "w") as archive:
            archive.writestr("[Content_Types].xml", content_types)
            archive.writestr("_rels/.rels", rels)
            archive.writestr("word/document.xml", document_xml)

    def _escape_xml(self, value: str) -> str:
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )
```

#### `backend/prompts/generation/diagram/architecture.yaml`

**Language hint:** `yaml`

```yaml
Output **PlantUML only** for a **system architecture / context** view.

Rules:
- Start with `@startuml` and end with `@enduml`.
- Use `!theme plain`.
- Use `package`, `component`, `database`, or `actor` notation as appropriate.
- Show only major systems and key dependencies supported by the evidence.
- Prefer a high-level diagram over detailed internals when evidence is incomplete.
- Keep the diagram readable and compact.
- Prefer at most 8 named components/actors unless the evidence clearly requires more.
- No markdown fences, no commentary, no explanatory prose.

**Document type:** {doc_type}
**Section title:** {section_title}
**Section description:** {section_description}
**Generation hints:** {generation_hints}

**Evidence (trimmed):**
{evidence_context}
```

#### `backend/prompts/generation/diagram/correction.yaml`

**Language hint:** `yaml`

```yaml
The following PlantUML failed to render. Fix only the diagram syntax and validity.

Rules:
- Output **PlantUML only**.
- Start with `@startuml` and end with `@enduml`.
- Do not include markdown fences.
- Do not include commentary or explanations.
- Preserve the original intent where possible.
- If the original is too broken, produce a smaller valid high-level diagram using only the supported evidence.

**Render error:**
{render_error}

**Failed PlantUML:**
{failed_diagram_source}

**Section title:** {section_title}

**Evidence summary (trimmed):**
{evidence_context}
```

#### `backend/prompts/generation/diagram/default.yaml`

**Language hint:** `yaml`

```yaml
You output **PlantUML only** (no markdown fences, no commentary).

Goal:
Create a compact, high-level architecture/process diagram strictly supported by the evidence.

Rules:
- Start with `@startuml` and end with `@enduml`.
- Use `!theme plain`.
- Prefer `package`, `component`, `actor`, and simple arrows.
- Do not invent systems, actors, or flows not supported by the evidence.
- If evidence is thin, produce a smaller high-level diagram rather than guessing.
- Keep the diagram readable and compact.
- Prefer at most 8 named components/actors unless the evidence clearly requires more.
- Do not include image URLs, HTML, markdown, or explanations.

**Document type:** {doc_type}
**Section title:** {section_title}
**Section description:** {section_description}
**Generation hints:** {generation_hints}

**Evidence (trimmed):**
{evidence_context}
```

#### `backend/prompts/generation/diagram/flowchart.yaml`

**Language hint:** `yaml`

```yaml
Output **PlantUML only** for an **activity / process flow** diagram.

Rules:
- Start with `@startuml` and end with `@enduml`.
- Use activity diagram syntax (`start`, `stop`, `if`, `endif`, `partition`) only when supported by evidence.
- Do not invent decision branches or process steps not evidenced.
- Prefer a short, high-level flow if details are incomplete.
- Keep the diagram readable and compact.
- Prefer at most 10 activity nodes unless the evidence clearly requires more.
- No markdown fences, no commentary, no explanatory prose.

**Document type:** {doc_type}
**Section title:** {section_title}
**Section description:** {section_description}
**Generation hints:** {generation_hints}

**Evidence (trimmed):**
{evidence_context}
```

#### `backend/prompts/generation/diagram/mermaid_default.yaml`

**Language hint:** `yaml`

```yaml
You output **Mermaid syntax only** (no markdown fences, no commentary).

Goal:
Create a compact high-level Mermaid diagram that reflects the evidence without inventing details.

Rules:
- Use `flowchart TD` unless another Mermaid form is clearly more appropriate.
- Use short node IDs and readable labels from the evidence.
- Do not use HTML tags.
- Omit unknown details rather than guessing.
- Keep the diagram readable and compact.
- Prefer at most 8 nodes unless the evidence clearly requires more.
- No markdown fences, no commentary, no explanatory prose.

**Document type:** {doc_type}
**Section title:** {section_title}
**Section description:** {section_description}
**Generation hints:** {generation_hints}

**Evidence (trimmed):**
{evidence_context}
```

#### `backend/prompts/generation/diagram/sequence.yaml`

**Language hint:** `yaml`

```yaml
Output **PlantUML only** for a **sequence diagram**.

Rules:
- Start with `@startuml` and end with `@enduml`.
- Use `autonumber`.
- Include only participants and messages supported by evidence.
- Omit uncertain messages rather than inventing them.
- Keep the sequence compact and readable.
- Prefer at most 6 participants unless the evidence clearly requires more.
- No markdown fences, no commentary, no explanatory prose.

**Document type:** {doc_type}
**Section title:** {section_title}
**Section description:** {section_description}
**Generation hints:** {generation_hints}

**Evidence (trimmed):**
{evidence_context}
```

#### `backend/prompts/generation/table/api_specification.yaml`

**Language hint:** `yaml`

```yaml
Produce an **API specification summary** as one GitHub-flavored markdown table (not OpenAPI YAML).

Columns exactly: {table_headers}
- Methods, paths, auth, and payloads must come from evidence; otherwise mark `TBD`.
- `Evidence` column with (Source n).

**Document type:** {doc_type}
**Section title:** {section_title}
**Section description:** {section_description}
**Generation hints:** {generation_hints}

**Evidence:**
{evidence_context}
```

#### `backend/prompts/generation/table/default.yaml`

**Language hint:** `yaml`

```yaml
You are filling a **markdown table** for an SDLC document section.

Output **only one GitHub-flavored markdown table**.
Do **not** add:
- an introductory sentence
- explanatory prose
- code fences
- analyst notes
- traceability commentary outside the table

**Rules:**
- Include exactly one header row and one separator row.
- Use exactly these column headers in order: {table_headers}
- If a value is unknown from evidence, use `TBD` rather than inventing facts.
- Keep cell text concise and enterprise-document appropriate.
- Add a final column `Evidence` with compact `(Source n)` references per row where applicable.
- Do not wrap the whole table or each line in bold/italic markdown.
- Do not output anything before or after the table.

**Document type:** {doc_type}
**Section title:** {section_title}
**Section description:** {section_description}
**Generation hints:** {generation_hints}
**Required fields (hints):** {required_fields}
**Expected length:** {expected_length}
**Tone:** {tone}
**Evidence:**
{evidence_context}
```

#### `backend/prompts/generation/table/risk_register.yaml`

**Language hint:** `yaml`

```yaml
Produce a **risk register** as one GitHub-flavored markdown table.

Columns exactly: {table_headers}
- Severity/Probability: Low/Medium/High or TBD.
- `Evidence` column: (Source n) references.

**Document type:** {doc_type}
**Section title:** {section_title}
**Section description:** {section_description}
**Generation hints:** {generation_hints}

**Evidence:**
{evidence_context}
```

#### `backend/prompts/generation/table/stakeholders.yaml`

**Language hint:** `yaml`

```yaml
Produce a **stakeholder / RACI-style** matrix as a single GitHub-flavored markdown table.

Columns must be exactly: {table_headers}
- Roles should reflect evidence; use `TBD` for unknown names.
- Last column `Evidence` with (Source n) per row.

**Document type:** {doc_type}
**Section title:** {section_title}
**Section description:** {section_description}
**Generation hints:** {generation_hints}

**Evidence:**
{evidence_context}
```

#### `backend/prompts/generation/table/traceability_matrix.yaml`

**Language hint:** `yaml`

```yaml
Produce a **requirements traceability matrix** as one GitHub-flavored markdown table.

Columns exactly: {table_headers}
- Link requirements or work items only when supported by evidence.
- Use `TBD` for unknown IDs.
- Include `Evidence` column with (Source n).

**Document type:** {doc_type}
**Section title:** {section_title}
**Section description:** {section_description}
**Generation hints:** {generation_hints}

**Evidence:**
{evidence_context}
```

#### `backend/prompts/generation/text/architecture.yaml`

**Language hint:** `yaml`

```yaml
You are a solution architect describing only the **architecture** relevant to this section.

Output **GitHub-flavored Markdown** only.

Rules:
- Focus on architecture-specific narrative only: major components, interfaces, and data flows that are supported by evidence.
- Do **not** restate general overview, requirements, risks, assumptions, or dependencies unless essential to the architecture explanation.
- Do **not** repeat the section title as a heading.
- Do **not** add traceability notes, source summaries, screenshot placeholders, or analyst comments.
- Keep the narrative concise and section-specific.
- If evidence is incomplete, identify the gap briefly rather than broadening the scope.

**Document type:** {doc_type}
**Section title:** {section_title}
**Section description:** {section_description}
**Generation hints:** {generation_hints}
**Expected length:** {expected_length}
**Tone:** {tone}
**Evidence:**
{evidence_context}
```

#### `backend/prompts/generation/text/assumptions.yaml`

**Language hint:** `yaml`

```yaml
You are documenting assumptions or dependencies only when this section explicitly requires them.

Output **GitHub-flavored Markdown** only.

Rules:
- Write only the assumptions/dependencies content relevant to this section.
- Do **not** repeat the section title as a heading.
- Do **not** add generic assumptions just to fill space.
- Include only assumptions or dependencies that are directly supported by evidence or clearly framed as unresolved constraints.
- Do not expand into broader risks, requirements, or solution design unless this section explicitly requires it.
- Do **not** add traceability notes, source summaries, screenshot placeholders, or analyst comments.
- Prefer concise bullets over nested markdown heading structures.

**Document type:** {doc_type}
**Section title:** {section_title}
**Section description:** {section_description}
**Generation hints:** {generation_hints}
**Expected length:** {expected_length}
**Tone:** {tone}
**Evidence:**
{evidence_context}
```

#### `backend/prompts/generation/text/default.yaml`

**Language hint:** `yaml`

```yaml
You are a senior technical writer producing one section body for an enterprise SDLC deliverable.You are a senior technical writer producing one section following assumptions..."
Output **GitHub-flavored Markdown** only, but follow these rules strictly.

Rules:
- Write **only the content for this section**.
- Do **not** repeat the section title as a markdown heading.
- Do **not** add traceability notes, source summaries, screenshot placeholders, or reviewer notes.
- Do **not** introduce subsections that belong to sibling or child sections.
- Use a formal, concise, enterprise-document tone suitable for a polished design or requirements deliverable.
- Avoid meta narration such as:
  - "This section defines..."
  - "This document captures..."
  - "This section provides high-level context..."
  - "The following risks..."
  - "Known gaps..."
  - "Next steps required..."
  unless the wording is strictly necessary to preserve meaning.
- Prefer direct, document-style prose over discovery-summary language.
- Prefer short paragraphs and compact lists over nested markdown heading structures.
- Use markdown headings only when absolutely necessary for readability, and never to repeat the current section title.
- If this section has child sections, keep this section high-level and do not pre-write their detailed content.
- If evidence is incomplete, state the gap briefly and move on; do not pad the section with generic assumptions.
- Do not invent requirements, controls, or architecture details not supported by evidence.
- Do not decorate every paragraph with markdown emphasis or bold/italic wrappers.

Hierarchy guidance:
- Parent section title: {parent_section_title}
- Child section titles: {child_section_titles}
- Section role: {section_role}

Additional hierarchy rules:
- If section role is **parent_with_children**, provide only framing or summary content for this section.
- Do not restate the detailed content that clearly belongs to child section titles listed above.
- If section role is **child_or_leaf**, focus only on this specific section and do not restate broader parent-level summaries.

**Document type:** {doc_type}
**Section title:** {section_title}
**Section description:** {section_description}
**Generation hints:** {generation_hints}
**Expected length:** {expected_length}
**Tone:** {tone}
**Retrieved evidence (with source markers — preserve meaning; do not copy verbatim large blocks):**
{evidence_context}

Produce polished prose for this section only.
```

#### `backend/prompts/generation/text/overview.yaml`

**Language hint:** `yaml`

```yaml
You are a senior enterprise architect writing the **Overview** section of a structured document.

Output **GitHub-flavored Markdown** only.

Rules:
- Write **only overview-level content** for this section.
- Cover the document purpose and a concise high-level context.
- Mention scope boundaries only briefly if they are essential to understanding the overview.
- Do **not** fully restate detailed scope, requirements, risks, assumptions, or dependencies if those belong to later sections.
- Do **not** repeat the section title as a heading.
- Do **not** add traceability notes, source summaries, screenshot placeholders, or analyst instructions.
- Prefer 2–4 short paragraphs and, if useful, one short bullet list.
- If evidence is incomplete, state the limitation briefly instead of expanding with generic filler.

**Document type:** {doc_type}
**Section title:** {section_title}
**Section description:** {section_description}
**Generation hints:** {generation_hints}
**Expected length:** {expected_length}
**Tone:** {tone}
**Evidence:**
{evidence_context}
```

#### `backend/prompts/generation/text/requirements.yaml`

**Language hint:** `yaml`

```yaml
You are a requirements engineer writing one requirements-focused section.

Output **GitHub-flavored Markdown** only.

Rules:
- Write only the requirements content relevant to this section title.
- Do **not** repeat the section title as a heading.
- Use a formal enterprise-document tone, not workshop-summary narration.
- Avoid meta lead-ins such as:
  - "This section summarizes..."
  - "Core capabilities required..."
  - "The following requirements..."
  - "Known gaps..."
  unless needed for readability.
- If the section title is broad (for example "Requirements"), provide only a concise framing summary.
- If the section title is specifically about functional requirements, provide functional requirements only.
- If the section title is specifically about non-functional requirements, provide non-functional constraints only.
- Do not automatically include both functional and non-functional requirements unless the section explicitly calls for both.
- Prefer concise numbered requirements when appropriate.
- Keep requirements testable and evidence-based.
- If evidence is incomplete, mark the gap briefly; do not invent standards, IDs, or controls.
- Do **not** add traceability notes, source summaries, screenshot placeholders, or analyst comments.
- Do not decorate every paragraph with markdown emphasis or bold/italic wrappers.

Hierarchy guidance:
- Parent section title: {parent_section_title}
- Child section titles: {child_section_titles}
- Section role: {section_role}

Additional hierarchy rules:
- If section role is **parent_with_children** and this section title is broad (for example "Requirements"),
  provide only a short umbrella summary and leave detailed requirement breakdowns to child sections.
- Do not restate the detailed content that belongs to child requirement subsections.

**Document type:** {doc_type}
**Section title:** {section_title}
**Section description:** {section_description}
**Generation hints:** {generation_hints}
**Expected length:** {expected_length}
**Tone:** {tone}
**Evidence:**
{evidence_context}
```

#### `backend/prompts/generation/text/risks.yaml`

**Language hint:** `yaml`

```yaml
You are documenting **risks** for a single section.You are documenting **risks** **GitHub-flavored Markdown** only.

Rules:
- Focus only on risks relevant to this section.
- Prefer a compact markdown table when there are multiple risks.
- Do **not** repeat the section title as a heading.
- Do **not** add traceability notes, source summaries, screenshot placeholders, or analyst comments.
- Keep mitigations specific and concise.
- Use Impact/Likelihood only when supported by evidence; otherwise use TBD.
- Do not restate assumptions, dependencies, or requirements unless they are directly necessary to describe the risk.

Suggested columns when using a table:
Risk | Impact | Likelihood | Mitigation

**Document type:** {doc_type}
**Section title:** {section_title}
**Section description:** {section_description}
**Generation hints:** {generation_hints}
**Expected length:** {expected_length}
**Tone:** {tone}
**Evidence:**
{evidence_context}
```

#### `backend/prompts/generation/text/scope.yaml`

**Language hint:** `yaml`

```yaml
You are defining **scope** for an SDLC document.

Output **GitHub-flavored Markdown** only.

Rules:
- Write only the scope content for this section.
- Prefer two labeled lists:
  - **In scope**
  - **Out of scope**
- Do **not** use markdown headings that repeat the section title.
- Do **not** add traceability notes, source summaries, screenshot placeholders, or analyst comments.
- Keep each bullet concise and evidence-based.
- If an item is uncertain, state it briefly as an unresolved boundary instead of inventing detail.
- Do not repeat detailed requirements, risks, or assumptions unless they are essential to scope boundaries.

**Document type:** {doc_type}
**Section title:** {section_title}
**Section description:** {section_description}
**Generation hints:** {generation_hints}
**Expected length:** {expected_length}
**Tone:** {tone}
**Evidence:**
{evidence_context}
```

#### `backend/prompts/template/classifier.yaml`

**Language hint:** `yaml`

```yaml
prompt: |
  You are a template compiler assistant.

  Classify each input heading into exactly one section object.
  Preserve the input order exactly.
  Return one output object per heading.
  Do not omit headings.
  Do not add extra keys.
  If unsure, use output_type = "text".

  Allowed output_type values:
  - text
  - table
  - diagram

  Return STRICT JSON only in this exact shape:
  {
    "sections": [
      {
        "heading": "string",
        "output_type": "text",
        "description": "short description",
        "prompt_selector": "default",
        "required_fields": [],
        "is_complex": false
      }
    ]
  }

  Notes:
  - The input may include [L1], [L2], [L3] markers. These indicate heading depth and are already determined by the compiler.
  - Do not reinterpret the hierarchy. Only classify the content type and section metadata.
  - If a heading sounds tabular, use "table".
  - If a heading clearly requests a diagram/architecture/flow/sequence/component view, use "diagram".
  - Otherwise use "text".

  Template title:
  $title

  Headings:
  $headings
```

#### `backend/pytest.ini`

**Language hint:** `ini`

```ini
[pytest]
pythonpath = .
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -q
```

#### `backend/repositories/__init__.py`

**Language hint:** `python`

```python
"""JSON file persistence."""

from repositories.document_repo import DocumentRepository
from repositories.output_repo import OutputRepository
from repositories.template_repo import TemplateRepository
from repositories.workflow_repo import WorkflowRepository

__all__ = [
    "DocumentRepository",
    "TemplateRepository",
    "WorkflowRepository",
    "OutputRepository",
]
```

#### `backend/repositories/base.py`

**Language hint:** `python`

```python
"""Generic JSON file repository."""

from __future__ import annotations

from pathlib import Path
from typing import Generic, TypeVar

import orjson
from pydantic import BaseModel

from core.exceptions import NotFoundException
from core.ids import utc_now_iso
from core.logging import get_logger

T = TypeVar("T", bound=BaseModel)
logger = get_logger(__name__)


class BaseJsonRepository(Generic[T]):
    def __init__(self, storage_path: Path, model_class: type[T]) -> None:
        self._path = storage_path
        self._model_class = model_class
        self._path.mkdir(parents=True, exist_ok=True)

    def _id_field(self) -> str:
        raise NotImplementedError

    def _file(self, record_id: str) -> Path:
        return self._path / f"{record_id}.json"

    def save(self, record: T) -> T:
        record_id = getattr(record, self._id_field())
        payload = record.model_dump()
        logger.info(
            "repository.save model=%s id=%s path=%s",
            self._model_class.__name__,
            record_id,
            self._file(record_id),
        )
        self._file(record_id).write_bytes(orjson.dumps(payload, option=orjson.OPT_INDENT_2))
        return record

    def get(self, record_id: str) -> T | None:
        file_path = self._file(record_id)
        if not file_path.is_file():
            logger.info(
                "repository.get.miss model=%s id=%s path=%s",
                self._model_class.__name__,
                record_id,
                file_path,
            )
            return None
        logger.info(
            "repository.get.hit model=%s id=%s path=%s",
            self._model_class.__name__,
            record_id,
            file_path,
        )
        data = orjson.loads(file_path.read_bytes())
        return self._model_class.model_validate(data)

    def get_or_raise(self, record_id: str, resource_name: str) -> T:
        record = self.get(record_id)
        if record is None:
            raise NotFoundException(resource_name, record_id)
        return record

    def list_all(self) -> list[T]:
        records: list[T] = []
        for file_path in self._path.glob("*.json"):
            data = orjson.loads(file_path.read_bytes())
            records.append(self._model_class.model_validate(data))
        records.sort(key=lambda rec: getattr(rec, "created_at", ""), reverse=True)
        logger.info(
            "repository.list_all model=%s path=%s total=%s",
            self._model_class.__name__,
            self._path,
            len(records),
        )
        return records

    def update(self, record_id: str, resource_name: str, **fields: object) -> T:
        logger.info(
            "repository.update.started model=%s id=%s fields=%s",
            self._model_class.__name__,
            record_id,
            sorted(fields.keys()),
        )
        record = self.get_or_raise(record_id, resource_name)
        current = record.model_dump()
        current.update(fields)
        if "updated_at" in current:
            current["updated_at"] = utc_now_iso()
        updated = self._model_class.model_validate(current)
        self.save(updated)
        logger.info(
            "repository.update.completed model=%s id=%s",
            self._model_class.__name__,
            record_id,
        )
        return updated

    def delete(self, record_id: str) -> bool:
        file_path = self._file(record_id)
        if not file_path.is_file():
            logger.info(
                "repository.delete.miss model=%s id=%s path=%s",
                self._model_class.__name__,
                record_id,
                file_path,
            )
            return False
        file_path.unlink()
        logger.info(
            "repository.delete.completed model=%s id=%s path=%s",
            self._model_class.__name__,
            record_id,
            file_path,
        )
        return True
```

#### `backend/repositories/document_models.py`

**Language hint:** `python`

```python
"""Document persistence model."""

from __future__ import annotations

from pydantic import BaseModel, Field

from core.constants import DocumentIngestionStatus, DocumentStatus


class DocumentRecord(BaseModel):
    document_id: str
    filename: str
    content_type: str
    size_bytes: int
    status: str = Field(default=DocumentStatus.READY)
    file_path: str
    created_at: str
    updated_at: str

    # Populated after Document Intelligence (first successful ingestion parse path).
    page_count: int | None = None
    language: str | None = None
    doc_intelligence_confidence: float | None = None

    # Ingest-once policy: index chunks under document_id; skip Phase 2 when INDEXED.
    ingestion_status: str = Field(default=DocumentIngestionStatus.NOT_STARTED)
    indexed_chunk_count: int | None = None
    indexed_at: str | None = None
    last_ingestion_error: str | None = None
```

#### `backend/repositories/document_repo.py`

**Language hint:** `python`

```python
"""Document JSON repository."""

from __future__ import annotations

from pathlib import Path

from repositories.base import BaseJsonRepository
from repositories.document_models import DocumentRecord


class DocumentRepository(BaseJsonRepository[DocumentRecord]):
    def __init__(self, storage_path: Path) -> None:
        super().__init__(storage_path=storage_path, model_class=DocumentRecord)

    def _id_field(self) -> str:
        return "document_id"

    def get_or_raise(self, document_id: str, resource_name: str = "Document") -> DocumentRecord:
        return super().get_or_raise(document_id, resource_name)

    def update(self, document_id: str, **fields: object) -> DocumentRecord:
        return super().update(document_id, resource_name="Document", **fields)
```

#### `backend/repositories/output_models.py`

**Language hint:** `python`

```python
"""Output persistence model."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class OutputRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    output_id: str
    workflow_run_id: str
    document_id: str
    doc_type: str
    output_format: str
    status: str
    file_path: str
    filename: str
    size_bytes: int
    created_at: str
    updated_at: str
    ready_at: str | None = None
```

#### `backend/repositories/output_repo.py`

**Language hint:** `python`

```python
"""Output JSON repository."""

from __future__ import annotations

from pathlib import Path

from repositories.base import BaseJsonRepository
from repositories.output_models import OutputRecord


class OutputRepository(BaseJsonRepository[OutputRecord]):
    def __init__(self, storage_path: Path) -> None:
        super().__init__(storage_path=storage_path, model_class=OutputRecord)

    def _id_field(self) -> str:
        return "output_id"

    def get_or_raise(self, output_id: str, resource_name: str = "Output") -> OutputRecord:
        return super().get_or_raise(output_id, resource_name)

    def update(self, output_id: str, **fields: object) -> OutputRecord:
        return super().update(output_id, resource_name="Output", **fields)
```

#### `backend/repositories/template_models.py`

**Language hint:** `python`

```python
"""Template persistence model."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from core.constants import TemplateSource, TemplateStatus


class TemplateRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    template_id: str
    filename: str
    template_type: str
    template_source: str = Field(default=TemplateSource.CUSTOM)
    version: str | None = None
    status: str = Field(default=TemplateStatus.PENDING)
    file_path: str | None = None
    preview_path: str | None = None
    preview_html: str | None = None
    compile_error: str | None = None
    compiled_at: str | None = None
    section_plan: list[dict[str, object]] = Field(default_factory=list)
    style_map: dict[str, object] = Field(default_factory=dict)
    sheet_map: dict[str, object] = Field(default_factory=dict)
    created_at: str
    updated_at: str
```

#### `backend/repositories/template_repo.py`

**Language hint:** `python`

```python
"""Template JSON repository."""

from __future__ import annotations

from pathlib import Path

from repositories.base import BaseJsonRepository
from repositories.template_models import TemplateRecord


class TemplateRepository(BaseJsonRepository[TemplateRecord]):
    def __init__(self, storage_path: Path) -> None:
        super().__init__(storage_path=storage_path, model_class=TemplateRecord)

    def _id_field(self) -> str:
        return "template_id"

    def get_or_raise(self, template_id: str, resource_name: str = "Template") -> TemplateRecord:
        return super().get_or_raise(template_id, resource_name)

    def update(self, template_id: str, **fields: object) -> TemplateRecord:
        return super().update(template_id, resource_name="Template", **fields)
```

#### `backend/repositories/workflow_models.py`

**Language hint:** `python`

```python
"""Workflow persistence model (minimal fields for guards and validation)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class WorkflowRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    workflow_run_id: str
    document_id: str
    template_id: str
    doc_type: str
    status: str = Field(default="PENDING")
    current_phase: str | None = None
    overall_progress_percent: float = 0.0
    current_step_label: str = ""
    output_id: str | None = None
    section_plan: list[dict[str, object]] = Field(default_factory=list)
    style_map: dict[str, object] = Field(default_factory=dict)
    sheet_map: dict[str, object] = Field(default_factory=dict)
    section_progress: dict[str, object] = Field(default_factory=dict)
    section_retrieval_results: dict[str, object] = Field(default_factory=dict)
    section_generation_results: dict[str, object] = Field(default_factory=dict)
    assembled_document: dict[str, object] = Field(default_factory=dict)
    observability_summary: dict[str, object] = Field(default_factory=dict)
    errors: list[dict[str, object]] = Field(default_factory=list)
    warnings: list[dict[str, object]] = Field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
```

#### `backend/repositories/workflow_repo.py`

**Language hint:** `python`

```python
"""Workflow JSON repository."""

from __future__ import annotations

from pathlib import Path

from repositories.base import BaseJsonRepository
from repositories.workflow_models import WorkflowRecord


class WorkflowRepository(BaseJsonRepository[WorkflowRecord]):
    def __init__(self, storage_path: Path) -> None:
        super().__init__(storage_path=storage_path, model_class=WorkflowRecord)

    def _id_field(self) -> str:
        return "workflow_run_id"

    def get_or_raise(self, workflow_run_id: str, resource_name: str = "Workflow") -> WorkflowRecord:
        return super().get_or_raise(workflow_run_id, resource_name)

    def update(self, workflow_run_id: str, **fields: object) -> WorkflowRecord:
        return super().update(workflow_run_id, resource_name="Workflow", **fields)

    def list_by_document(self, document_id: str) -> list[WorkflowRecord]:
        return [w for w in self.list_all() if w.document_id == document_id]
```

#### `backend/requirements.txt`

**Language hint:** `text`

```text
# Minimal deps for foundation modules (expand to match docs/03 as the app grows).
pydantic>=2.7.0,<3
pydantic-settings>=2.2.0,<3
fastapi>=0.111.0,<1
orjson>=3.10.0,<4
pytest>=8.2.0,<9
httpx>=0.27.0,<1
python-multipart>=0.0.26,<1
tiktoken>=0.7.0,<1
python-docx>=1.1.0,<2
openpyxl>=3.1.0,<4
uvicorn[standard]>=0.30.0,<1
openai>=1.40.0,<2
semantic

# API / validation / settings
fastapi>=0.115,<1.0
uvicorn[standard]>=0.30,<1.0
python-multipart>=0.0.9,<1.0
pydantic>=2.8,<3.0
pydantic-settings>=2.4,<3.0
python-dotenv>=1.0,<2.0

# Structured logging / serialization
structlog>=24.0,<26.0
orjson>=3.10,<4.0

# Azure + AI
semantic-kernel>=1.30,<2.0
openai>=1.40,<2.0
azure-identity>=1.17,<2.0
azure-search-documents>=11.6,<12.0
azure-ai-documentintelligence>=1.0,<2.0
azure-storage-blob>=12.22,<13.0

# HTTP / async / retry helpers
httpx>=0.27,<1.0
aiohttp>=3.10,<4.0
tenacity>=8.5,<10.0

# Token budgeting / document rendering / images
tiktoken>=0.8,<1.0
python-docx>=1.1,<2.0
pillow>=10.4,<12.0
lxml>=5.3,<6.0
pyyaml
```

#### `backend/scripts/ai_search_index.py`

**Language hint:** `python`

```python
import json
import os
import sys
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
load_dotenv()

ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "").rstrip("/")
API_KEY = os.getenv("AZURE_SEARCH_API_KEY", "").strip()
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME", "sdlc-chunks").strip()
API_VERSION = os.getenv("AZURE_SEARCH_API_VERSION", "2025-09-01").strip()
VECTOR_DIMENSIONS = int(os.getenv("AZURE_SEARCH_VECTOR_DIMENSIONS", "1536"))

TIMEOUT = 60


def require_config() -> None:
    missing = []
    if not ENDPOINT:
        missing.append("AZURE_SEARCH_ENDPOINT")
    if not API_KEY:
        missing.append("AZURE_SEARCH_API_KEY")
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")


def build_url(path: str) -> str:
    return f"{ENDPOINT}{path}?api-version={API_VERSION}"


def headers() -> Dict[str, str]:
    return {
        "Content-Type": "application/json",
        "api-key": API_KEY,
    }


def request(method: str, path: str, expected_statuses: List[int], **kwargs) -> Any:
    response = requests.request(
        method=method,
        url=build_url(path),
        headers=headers(),
        timeout=TIMEOUT,
        **kwargs,
    )

    if response.status_code not in expected_statuses:
        print("\n=== REQUEST FAILED ===")
        print(f"{method} {build_url(path)}")
        print(f"Status: {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2))
        except Exception:
            print(response.text)
        response.raise_for_status()

    if not response.text:
        return None

    try:
        return response.json()
    except Exception:
        return response.text


def list_indexes() -> List[str]:
    data = request("GET", "/indexes", [200])
    names = [item["name"] for item in data.get("value", [])]
    print("\nExisting indexes:")
    if not names:
        print("  (none)")
    else:
        for name in names:
            print(f"  - {name}")
    return names


def delete_index_if_exists(index_name: str) -> None:
    names = list_indexes()
    if index_name not in names:
        print(f"\nIndex '{index_name}' does not exist. Nothing to delete.")
        return

    print(f"\nDeleting index '{index_name}'...")
    request("DELETE", f"/indexes/{index_name}", [204])
    print(f"Deleted index '{index_name}'.")


def build_index_schema(index_name: str) -> Dict[str, Any]:
    return {
        "name": index_name,
        "description": "Chunk index for SDLC document ingestion and hybrid retrieval.",
        "fields": [
            {
                "name": "chunk_id",
                "type": "Edm.String",
                "key": True,
                "searchable": False,
                "filterable": True,
                "sortable": False,
                "facetable": False,
                "retrievable": True,
            },
            {
                "name": "document_id",
                "type": "Edm.String",
                "searchable": False,
                "filterable": True,
                "sortable": False,
                "facetable": False,
                "retrievable": True,
            },
            {
                "name": "workflow_run_id",
                "type": "Edm.String",
                "searchable": False,
                "filterable": True,
                "sortable": False,
                "facetable": False,
                "retrievable": True,
            },
            {
                "name": "text",
                "type": "Edm.String",
                "searchable": True,
                "filterable": False,
                "sortable": False,
                "facetable": False,
                "retrievable": True,
            },
            {
                "name": "chunk_index",
                "type": "Edm.Int32",
                "searchable": False,
                "filterable": True,
                "sortable": True,
                "facetable": False,
                "retrievable": True,
            },
            {
                "name": "section_heading",
                "type": "Edm.String",
                "searchable": False,
                "filterable": False,
                "sortable": False,
                "facetable": False,
                "retrievable": True,
            },
            {
                "name": "page_number",
                "type": "Edm.Int32",
                "searchable": False,
                "filterable": True,
                "sortable": True,
                "facetable": False,
                "retrievable": True,
            },
            {
                "name": "content_type",
                "type": "Edm.String",
                "searchable": False,
                "filterable": True,
                "sortable": False,
                "facetable": True,
                "retrievable": True,
            },
            {
                "name": "embedding",
                "type": "Collection(Edm.Single)",
                "searchable": True,
                "filterable": False,
                "sortable": False,
                "facetable": False,
                "retrievable": False,
                "stored": False,
                "dimensions": VECTOR_DIMENSIONS,
                "vectorSearchProfile": "vector-profile",
            },
        ],
        "vectorSearch": {
            "algorithms": [
                {
                    "name": "hnsw-config",
                    "kind": "hnsw",
                    "hnswParameters": {
                        "m": 4,
                        "efConstruction": 400,
                        "efSearch": 500,
                        "metric": "cosine",
                    },
                }
            ],
            "profiles": [
                {
                    "name": "vector-profile",
                    "algorithm": "hnsw-config",
                }
            ],
        },
    }


def create_index(index_name: str) -> None:
    schema = build_index_schema(index_name)
    print(f"\nCreating index '{index_name}' with API version {API_VERSION}...")
    result = request("POST", "/indexes", [201], json=schema)
    print(f"Created index: {result.get('name', index_name)}")


def get_index(index_name: str) -> Dict[str, Any]:
    return request("GET", f"/indexes/{index_name}", [200])


def main() -> None:
    require_config()

    print("=== Azure AI Search Recreate Index ===")
    print(f"Endpoint          : {ENDPOINT}")
    print(f"Index name        : {INDEX_NAME}")
    print(f"API version       : {API_VERSION}")
    print(f"Vector dimensions : {VECTOR_DIMENSIONS}")

    delete_index_if_exists(INDEX_NAME)
    create_index(INDEX_NAME)

    print("\nFetching created index for confirmation...")
    created = get_index(INDEX_NAME)
    print(json.dumps(
        {
            "name": created.get("name"),
            "field_count": len(created.get("fields", [])),
            "vectorSearch": created.get("vectorSearch", {}),
        },
        indent=2
    ))

    print("\nFinal index list:")
    list_indexes()
    print("\nDone.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nFATAL: {exc}")
        sys.exit(1)
```

#### `backend/scripts/validate_ai_search_index.py`

**Language hint:** `python`

```python
import json
import os
import sys
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv
load_dotenv()

ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "").rstrip("/")
API_KEY = os.getenv("AZURE_SEARCH_API_KEY", "").strip()
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME", "sdlc-chunks").strip()
API_VERSION = os.getenv("AZURE_SEARCH_API_VERSION", "2025-09-01").strip()
EXPECTED_DIMENSIONS = int(os.getenv("AZURE_SEARCH_VECTOR_DIMENSIONS", "1536"))

TIMEOUT = 60


def require_config() -> None:
    missing = []
    if not ENDPOINT:
        missing.append("AZURE_SEARCH_ENDPOINT")
    if not API_KEY:
        missing.append("AZURE_SEARCH_API_KEY")
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")


def build_url(path: str) -> str:
    return f"{ENDPOINT}{path}?api-version={API_VERSION}"


def headers() -> Dict[str, str]:
    return {
        "Content-Type": "application/json",
        "api-key": API_KEY,
    }


def request(method: str, path: str, expected_statuses: List[int], **kwargs) -> Any:
    response = requests.request(
        method=method,
        url=build_url(path),
        headers=headers(),
        timeout=TIMEOUT,
        **kwargs,
    )

    if response.status_code not in expected_statuses:
        print("\n=== REQUEST FAILED ===")
        print(f"{method} {build_url(path)}")
        print(f"Status: {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2))
        except Exception:
            print(response.text)
        response.raise_for_status()

    if not response.text:
        return None

    try:
        return response.json()
    except Exception:
        return response.text


def get_index(index_name: str) -> Dict[str, Any]:
    return request("GET", f"/indexes/{index_name}", [200])


def get_field(index_def: Dict[str, Any], field_name: str) -> Optional[Dict[str, Any]]:
    for field in index_def.get("fields", []):
        if field.get("name") == field_name:
            return field
    return None


def check_equal(errors: List[str], actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        errors.append(f"{label}: expected {expected!r}, got {actual!r}")


def check_true(errors: List[str], actual: Any, label: str) -> None:
    if actual is not True:
        errors.append(f"{label}: expected True, got {actual!r}")


def check_false(errors: List[str], actual: Any, label: str) -> None:
    if actual is not False:
        errors.append(f"{label}: expected False, got {actual!r}")


def validate_schema(index_def: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    # Required fields and core checks
    required_fields = {
        "chunk_id": "Edm.String",
        "document_id": "Edm.String",
        "workflow_run_id": "Edm.String",
        "text": "Edm.String",
        "chunk_index": "Edm.Int32",
        "section_heading": "Edm.String",
        "page_number": "Edm.Int32",
        "content_type": "Edm.String",
        "embedding": "Collection(Edm.Single)",
    }

    for field_name, expected_type in required_fields.items():
        field = get_field(index_def, field_name)
        if not field:
            errors.append(f"Missing field: {field_name}")
            continue
        check_equal(errors, field.get("type"), expected_type, f"{field_name}.type")

    # chunk_id
    field = get_field(index_def, "chunk_id")
    if field:
        check_true(errors, field.get("key"), "chunk_id.key")
        check_true(errors, field.get("filterable"), "chunk_id.filterable")

    # document_id
    field = get_field(index_def, "document_id")
    if field:
        check_true(errors, field.get("filterable"), "document_id.filterable")

    # workflow_run_id
    field = get_field(index_def, "workflow_run_id")
    if field:
        check_true(errors, field.get("filterable"), "workflow_run_id.filterable")

    # text
    field = get_field(index_def, "text")
    if field:
        check_true(errors, field.get("searchable"), "text.searchable")

    # chunk_index
    field = get_field(index_def, "chunk_index")
    if field:
        check_true(errors, field.get("filterable"), "chunk_index.filterable")
        check_true(errors, field.get("sortable"), "chunk_index.sortable")

    # page_number
    field = get_field(index_def, "page_number")
    if field:
        check_true(errors, field.get("filterable"), "page_number.filterable")
        check_true(errors, field.get("sortable"), "page_number.sortable")

    # content_type
    field = get_field(index_def, "content_type")
    if field:
        check_true(errors, field.get("filterable"), "content_type.filterable")

    # embedding
    field = get_field(index_def, "embedding")
    if field:
        check_true(errors, field.get("searchable"), "embedding.searchable")
        check_false(errors, field.get("filterable"), "embedding.filterable")
        check_false(errors, field.get("sortable"), "embedding.sortable")
        check_false(errors, field.get("facetable"), "embedding.facetable")
        check_equal(errors, field.get("dimensions"), EXPECTED_DIMENSIONS, "embedding.dimensions")
        check_equal(errors, field.get("vectorSearchProfile"), "vector-profile", "embedding.vectorSearchProfile")

    # vectorSearch config
    vector_search = index_def.get("vectorSearch", {})
    algorithms = vector_search.get("algorithms", [])
    profiles = vector_search.get("profiles", [])

    algo_names = {a.get("name"): a for a in algorithms if a.get("name")}
    profile_names = {p.get("name"): p for p in profiles if p.get("name")}

    if "hnsw-config" not in algo_names:
        errors.append("vectorSearch.algorithms missing 'hnsw-config'")
    else:
        check_equal(errors, algo_names["hnsw-config"].get("kind"), "hnsw", "vectorSearch.algorithms[hnsw-config].kind")

    if "vector-profile" not in profile_names:
        errors.append("vectorSearch.profiles missing 'vector-profile'")
    else:
        check_equal(
            errors,
            profile_names["vector-profile"].get("algorithm"),
            "hnsw-config",
            "vectorSearch.profiles[vector-profile].algorithm",
        )

    return errors


def main() -> None:
    require_config()

    print("=== Azure AI Search Schema Validator ===")
    print(f"Endpoint            : {ENDPOINT}")
    print(f"Index name          : {INDEX_NAME}")
    print(f"API version         : {API_VERSION}")
    print(f"Expected dimensions : {EXPECTED_DIMENSIONS}")

    index_def = get_index(INDEX_NAME)

    print("\nLive schema summary:")
    print(json.dumps(
        {
            "name": index_def.get("name"),
            "field_names": [f.get("name") for f in index_def.get("fields", [])],
            "vectorSearch": index_def.get("vectorSearch", {}),
        },
        indent=2
    ))

    errors = validate_schema(index_def)

    if errors:
        print("\n❌ VALIDATION FAILED")
        for err in errors:
            print(f" - {err}")
        sys.exit(1)

    print("\n✅ VALIDATION PASSED")
    print("The live index schema matches the expected backend contract.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nFATAL: {exc}")
        sys.exit(1)
```

#### `backend/services/__init__.py`

**Language hint:** `python`

```python
"""Application services (orchestration)."""
```

#### `backend/services/document_service.py`

**Language hint:** `python`

```python
"""Document service for BRD file metadata + storage operations."""

from __future__ import annotations

from pathlib import Path

from core.constants import WorkflowStatus
from core.ids import document_id, utc_now_iso
from core.logging import get_logger
from core.exceptions import ValidationException
from repositories.document_models import DocumentRecord
from repositories.document_repo import DocumentRepository
from repositories.workflow_repo import WorkflowRepository

logger = get_logger(__name__)


class DocumentService:
    def __init__(self, repo: DocumentRepository, workflow_repo: WorkflowRepository | None = None) -> None:
        self._repo = repo
        self._workflow_repo = workflow_repo

    def save_document(self, *, filename: str, content_type: str, payload: bytes) -> DocumentRecord:
        now = utc_now_iso()
        new_id = document_id()
        file_path = self._repo._path / f"{new_id}.bin"
        file_path.write_bytes(payload)

        record = DocumentRecord(
            document_id=new_id,
            filename=filename,
            content_type=content_type,
            size_bytes=len(payload),
            status="READY",
            file_path=file_path.name,
            created_at=now,
            updated_at=now,
        )
        self._repo.save(record)
        return record

    def list_all(self) -> list[DocumentRecord]:
        return self._repo.list_all()

    def get_or_raise(self, document_id: str) -> DocumentRecord:
        return self._repo.get_or_raise(document_id)

    def get_file_path(self, document_id: str) -> Path:
        record = self.get_or_raise(document_id)
        return self._repo._path / record.file_path

    def delete(self, document_id: str) -> bool:
        if self._workflow_repo is not None:
            workflows = self._workflow_repo.list_by_document(document_id)
            running = [item.workflow_run_id for item in workflows if item.status == WorkflowStatus.RUNNING]
            if running:
                raise ValidationException(
                    f"Cannot delete document {document_id}; workflow(s) still running: {', '.join(running)}",
                )

        record = self.get_or_raise(document_id)
        file_path = self._repo._path / record.file_path
        if file_path.exists():
            file_path.unlink()
        else:
            logger.warning("document.binary.missing document_id=%s file_path=%s", document_id, str(file_path))
        return self._repo.delete(document_id)
```

#### `backend/services/event_service.py`

**Language hint:** `python`

```python
"""In-memory event service for SSE subscribers."""

from __future__ import annotations

import asyncio

from core.ids import utc_now_iso


class EventService:
    def __init__(self) -> None:
        self._queues: dict[str, list[asyncio.Queue[dict[str, object]]]] = {}

    def subscribe(self, workflow_run_id: str) -> asyncio.Queue[dict[str, object]]:
        queue: asyncio.Queue[dict[str, object]] = asyncio.Queue(maxsize=200)
        self._queues.setdefault(workflow_run_id, []).append(queue)
        return queue

    def unsubscribe(self, workflow_run_id: str, queue: asyncio.Queue[dict[str, object]]) -> None:
        queues = self._queues.get(workflow_run_id, [])
        if queue in queues:
            queues.remove(queue)
        if not queues and workflow_run_id in self._queues:
            del self._queues[workflow_run_id]

    async def emit(self, workflow_run_id: str, event_type: str, payload: dict[str, object] | None = None) -> None:
        event = {
            "type": event_type,
            "workflow_run_id": workflow_run_id,
            "timestamp": utc_now_iso(),
            **(payload or {}),
        }
        for queue in list(self._queues.get(workflow_run_id, [])):
            if queue.full():
                continue
            queue.put_nowait(event)

    def subscriber_count(self, workflow_run_id: str) -> int:
        return len(self._queues.get(workflow_run_id, []))
```

#### `backend/services/output_service.py`

**Language hint:** `python`

```python
"""Output service for generated artifact records."""

from __future__ import annotations

from pathlib import Path

from core.ids import output_id, utc_now_iso
from core.constants import OutputFormat
from core.exceptions import ValidationException
from repositories.output_models import OutputRecord
from repositories.output_repo import OutputRepository


class OutputService:
    def __init__(self, repo: OutputRepository) -> None:
        self._repo = repo

    def create(
        self,
        *,
        workflow_run_id: str,
        document_id: str,
        doc_type: str,
        file_path: Path,
        filename: str,
    ) -> OutputRecord:
        extension = file_path.suffix.lower()
        if extension == ".docx":
            output_format = OutputFormat.DOCX.value
        elif extension == ".xlsx":
            output_format = OutputFormat.XLSX.value
        else:
            raise ValidationException(f"Unsupported output extension: {extension}")

        now = utc_now_iso()
        record = OutputRecord(
            output_id=output_id(),
            workflow_run_id=workflow_run_id,
            document_id=document_id,
            doc_type=doc_type,
            output_format=output_format,
            status="READY",
            file_path=str(file_path),
            filename=filename,
            size_bytes=file_path.stat().st_size if file_path.exists() else 0,
            created_at=now,
            updated_at=now,
            ready_at=now,
        )
        return self._repo.save(record)

    def get_or_raise(self, output_id_value: str) -> OutputRecord:
        return self._repo.get_or_raise(output_id_value)

    def get_download_info(self, output_id_value: str) -> tuple[Path, str]:
        record = self.get_or_raise(output_id_value)
        path = Path(record.file_path)
        if not path.exists():
            raise ValidationException(f"Output file does not exist for {output_id_value}")
        return path, record.filename
```

#### `backend/services/policy.py`

**Language hint:** `python`

```python
"""Cross-cutting API rules (validation and delete guards)."""

from __future__ import annotations

from core.constants import WorkflowStatus
from core.exceptions import ValidationException
from repositories.workflow_models import WorkflowRecord


def ensure_doc_type_matches_template(*, template_type: str, doc_type: str) -> None:
    """Reject workflow creation when template PDD/SDD/UAT does not match resolved doc_type."""
    if template_type != doc_type:
        raise ValidationException(
            "Template type does not match the selected document type. "
            "Upload or choose a matching template and try again.",
        )


def ensure_document_safe_to_delete(workflows_for_document: list[WorkflowRecord]) -> None:
    """Block delete while any workflow for this BRD is RUNNING (v1 single-node)."""
    running = [w for w in workflows_for_document if w.status == WorkflowStatus.RUNNING]
    if running:
        raise ValidationException(
            "Cannot delete this document while a workflow is still running against it.",
        )
```

#### `backend/services/template_service.py`

**Language hint:** `python`

```python
"""Template service for custom template files and compile lifecycle."""

from __future__ import annotations

from pathlib import Path

from core.constants import TemplateStatus
from core.ids import template_id, utc_now_iso
from core.logging import get_logger
from core.exceptions import TemplateException
from infrastructure.sk_adapter import AzureSKAdapter
from modules.template.classifier import TemplateClassifier
from modules.template.extractor import TemplateExtractor
from modules.template.models import StyleMap
from modules.template.planner import SectionPlanner
from modules.template.preview_generator import TemplatePreviewGenerator
from repositories.template_models import TemplateRecord
from repositories.template_repo import TemplateRepository

logger = get_logger(__name__)


class TemplateService:
    def __init__(
        self,
        repo: TemplateRepository,
        *,
        extractor: TemplateExtractor | None = None,
        classifier: TemplateClassifier | None = None,
        planner: SectionPlanner | None = None,
        preview_generator: TemplatePreviewGenerator | None = None,
        sk_adapter: AzureSKAdapter | None = None,
    ) -> None:
        self._repo = repo
        self._extractor = extractor or TemplateExtractor()
        adapter = sk_adapter or AzureSKAdapter()
        self._classifier = classifier or TemplateClassifier(adapter)
        self._planner = planner or SectionPlanner()
        self._preview_generator = preview_generator or TemplatePreviewGenerator()

    def save_template(
        self,
        *,
        filename: str,
        template_type: str,
        payload: bytes,
        version: str | None = None,
    ) -> TemplateRecord:
        now = utc_now_iso()
        new_id = template_id()

        file_path = self._repo._path / f"{new_id}.bin"
        file_path.write_bytes(payload)

        record = TemplateRecord(
            template_id=new_id,
            filename=filename,
            template_type=template_type,
            version=version,
            status=TemplateStatus.COMPILING.value,
            file_path=file_path.name,
            created_at=now,
            updated_at=now,
        )
        return self._repo.save(record)

    async def compile_template(self, template_id_value: str) -> TemplateRecord:
        record = self.get_or_raise(template_id_value)

        if record.status not in {
            TemplateStatus.COMPILING.value,
            TemplateStatus.PENDING.value,
        }:
            return record

        preview_file: Path | None = None

        try:
            file_path = self.get_file_path(template_id_value)
            suffix = Path(record.filename).suffix.lower()

            if suffix == ".docx":
                skeleton, style_map, sheet_map = self._extractor.extract_docx(file_path)
            elif suffix == ".xlsx":
                skeleton, style_map, sheet_map = self._extractor.extract_xlsx(file_path)
            else:
                raise TemplateException(f"Unsupported template file type: {record.filename}")

            classifications = await self._classifier.classify_sections(skeleton)
            section_plan = self._planner.build_from_skeleton_and_classifications(
                skeleton,
                classifications,
            )

            preview_html: str | None = None
            preview_path: str | None = None

            if suffix == ".docx":
                preview_file = self._repo._path / f"{template_id_value}_preview.docx"
                self._preview_generator.build_preview_docx(
                    destination=preview_file,
                    title=skeleton.title,
                    section_plan=section_plan,
                )
                preview_path = preview_file.name
            else:
                preview_html = self._preview_generator.build_preview_html_from_xlsx(skeleton)

            return self._repo.update(
                template_id_value,
                status=TemplateStatus.READY.value,
                compiled_at=utc_now_iso(),
                compile_error=None,
                section_plan=[section.model_dump() for section in section_plan],
                style_map=style_map.model_dump(),
                sheet_map=sheet_map,
                preview_path=preview_path,
                preview_html=preview_html,
            )

        except Exception as exc:
            logger.exception("template.compile.failed template_id=%s", template_id_value)

            # IMPORTANT:
            # Remove failed templates completely instead of keeping them with FAILED status.
            self._cleanup_failed_template(record=record, preview_file=preview_file)

            raise TemplateException(
                f"Template compile failed and template was removed: {template_id_value}"
            ) from exc

    def list_all(self) -> list[TemplateRecord]:
        return self._repo.list_all()

    def get_or_raise(self, template_id_value: str) -> TemplateRecord:
        return self._repo.get_or_raise(template_id_value)

    def get_file_path(self, template_id_value: str) -> Path:
        record = self.get_or_raise(template_id_value)
        if not record.file_path:
            raise TemplateException(f"Template has no file path: {template_id_value}")
        return self._repo._path / record.file_path

    def get_preview_html(self, template_id_value: str) -> str:
        record = self.get_or_raise(template_id_value)
        if record.preview_html:
            return record.preview_html

        preview = record.preview_path or f"Template {template_id_value} preview is not generated yet."
        return f"<div><strong>{record.filename}</strong><p>{preview}</p></div>"

    def delete(self, template_id_value: str) -> bool:
        record = self.get_or_raise(template_id_value)

        # Delete both binary and preview artifacts if present
        for relative_path in [record.file_path, record.preview_path]:
            if not relative_path:
                continue

            path = self._repo._path / relative_path
            if path.exists():
                path.unlink()
            else:
                logger.warning(
                    "template.file.missing template_id=%s file_path=%s",
                    template_id_value,
                    str(path),
                )

        return self._repo.delete(template_id_value)

    def _cleanup_failed_template(self, *, record: TemplateRecord, preview_file: Path | None) -> None:
        """
        Delete failed template artifacts and remove the record from the repository.
        """
        paths_to_delete: list[Path] = []

        if record.file_path:
            paths_to_delete.append(self._repo._path / record.file_path)

        if record.preview_path:
            paths_to_delete.append(self._repo._path / record.preview_path)

        if preview_file is not None:
            paths_to_delete.append(preview_file)

        seen: set[Path] = set()
        for path in paths_to_delete:
            if path in seen:
                continue
            seen.add(path)

            try:
                if path.exists():
                    path.unlink()
                    logger.info(
                        "template.cleanup.file.deleted template_id=%s path=%s",
                        record.template_id,
                        str(path),
                    )
            except Exception:
                logger.exception(
                    "template.cleanup.file.delete_failed template_id=%s path=%s",
                    record.template_id,
                    str(path),
                )

        try:
            self._repo.delete(record.template_id)
            logger.info("template.cleanup.record.deleted template_id=%s", record.template_id)
        except Exception:
            logger.exception(
                "template.cleanup.record.delete_failed template_id=%s",
                record.template_id,
            )
```

#### `backend/services/workflow_executor.py`

**Language hint:** `python`

```python
"""Workflow executor skeleton for Phase 3."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from core.constants import MODEL_PRICING, PHASE_WEIGHTS, TemplateStatus, WorkflowPhase, WorkflowStatus
from core.exceptions import WorkflowException
from core.ids import utc_now_iso
from modules.ingestion.ingestion_coordinator import IngestionCoordinator, IngestionRunResult
from modules.ingestion.orchestrator import IngestionOrchestrator
from modules.generation.cost_tracking import GenerationCostTracker
from modules.generation.models import GenerationSectionResult
from modules.generation.observability import merge_generation_observability
from modules.generation.orchestrator import GenerationOrchestrator
from modules.observability.cost_rollup import merge_full_cost_summary
from modules.assembly.assembler import DocumentAssembler
from modules.assembly.models import AssembledDocument
from modules.export.renderer import ExportRenderer
from modules.export.types import ExportDocumentInfo, ExportTemplateInfo
from modules.retrieval.packager import EvidencePackager
from modules.retrieval.retriever import SectionRetriever, merge_retrieval_observability
from modules.template.inbuilt.registry import (
    doc_type_for_inbuilt_template,
    get_inbuilt_section_plan,
    get_inbuilt_style_map,
    is_inbuilt_template_id,
)
from modules.template.models import SectionDefinition, StyleMap
from repositories.document_models import DocumentRecord
from core.config import settings
from core.logging import get_logger
from services.event_service import EventService
from services.output_service import OutputService
from services.workflow_service import WorkflowService

logger = get_logger(__name__)


@dataclass(slots=True)
class _RetrievalCostTracker:
    llm_cost_usd: float = 0.0
    total_tokens_in: int = 0
    total_tokens_out: int = 0
    total_llm_calls: int = 0

    def track_call(self, *, model: str, task: str, input_tokens: int, output_tokens: int) -> None:
        del task
        rates = MODEL_PRICING.get(model)
        if rates is None:
            return
        self.total_tokens_in += int(input_tokens)
        self.total_tokens_out += int(output_tokens)
        self.total_llm_calls += 1
        self.llm_cost_usd += (input_tokens / 1000.0) * rates["input"] + (output_tokens / 1000.0) * rates["output"]


class WorkflowExecutor:
    def __init__(
        self,
        workflow_service: WorkflowService,
        event_service: EventService,
        ingestion_orchestrator: IngestionOrchestrator | None = None,
        ingestion_coordinator: IngestionCoordinator | None = None,
        section_retriever: SectionRetriever | None = None,
        evidence_packager: EvidencePackager | None = None,
        generation_orchestrator: GenerationOrchestrator | None = None,
        output_service: OutputService | None = None,
        document_assembler: DocumentAssembler | None = None,
        export_renderer: ExportRenderer | None = None,
    ) -> None:
        self._workflow_service = workflow_service
        self._event_service = event_service
        self._ingestion_orchestrator = ingestion_orchestrator
        self._ingestion_coordinator = ingestion_coordinator
        self._section_retriever = section_retriever
        self._evidence_packager = evidence_packager
        self._generation_orchestrator = generation_orchestrator
        self._output_service = output_service
        self._document_assembler = document_assembler or DocumentAssembler()
        self._export_renderer = export_renderer or ExportRenderer(settings.storage_root)

        # Phase 2: limit retrieval fan-out against Azure AI Search
        self._max_concurrent_retrieval_sections = max(
            1,
            int(getattr(settings, "retrieval_max_concurrent_sections", 3)),
        )
        self._retrieval_semaphore = asyncio.Semaphore(self._max_concurrent_retrieval_sections)

    async def _run_phase(
        self,
        workflow_run_id: str,
        phase: WorkflowPhase,
        fn: Callable[[str], Awaitable[None]],
    ) -> None:
        logger.info(
            "phase.started workflow_run_id=%s phase=%s",
            workflow_run_id,
            phase.value,
        )
        self._workflow_service.update(
            workflow_run_id,
            current_phase=phase.value,
            current_step_label=f"{phase.value} started",
        )
        await self._event_service.emit(
            workflow_run_id,
            "phase.started",
            {"phase": phase.value},
        )

        phase_started_at = perf_counter()
        for attempt in range(2):
            try:
                logger.info(
                    "phase.attempt workflow_run_id=%s phase=%s attempt=%s",
                    workflow_run_id,
                    phase.value,
                    attempt + 1,
                )
                await fn(workflow_run_id)
                break
            except Exception as exc:
                logger.exception(
                    "phase.attempt_failed workflow_run_id=%s phase=%s attempt=%s error=%s",
                    workflow_run_id,
                    phase.value,
                    attempt + 1,
                    str(exc),
                )
                if attempt == 0:
                    await asyncio.sleep(2)
                    continue
                raise WorkflowException(
                    f"Phase failed after retry ({phase.value}): {exc}",
                    code="WORKFLOW_PHASE_ERROR",
                ) from exc

        workflow = self._workflow_service.get_or_raise(workflow_run_id)
        progress = min(100.0, float(workflow.overall_progress_percent) + PHASE_WEIGHTS[phase])
        duration_ms = int((perf_counter() - phase_started_at) * 1000)
        self._workflow_service.update(
            workflow_run_id,
            overall_progress_percent=progress,
            current_step_label=f"{phase.value} completed",
        )
        await self._event_service.emit(
            workflow_run_id,
            "phase.completed",
            {"phase": phase.value, "duration_ms": duration_ms},
        )
        logger.info(
            "phase.completed workflow_run_id=%s phase=%s progress=%s duration_ms=%s",
            workflow_run_id,
            phase.value,
            progress,
            duration_ms,
        )
    async def _run_retrieval_with_semaphore(self, coro):
        async with self._retrieval_semaphore:
            return await coro

    async def _phase_input_preparation(self, workflow_run_id: str) -> None:
        logger.info("inputpreparation.phase.enter workflow_run_id=%s", workflow_run_id)
        self._workflow_service.update(workflow_run_id, current_step_label="Initializing workflow")
        logger.info("inputpreparation.phase.completed workflow_run_id=%s", workflow_run_id)

    async def _phase_ingestion(self, workflow_run_id: str) -> None:
        workflow = self._workflow_service.get_or_raise(workflow_run_id)
        document = self._workflow_service.get_document(workflow.document_id)
        logger.info(
            "ingestion.enter workflow_run_id=%s document_id=%s",
            workflow_run_id,
            workflow.document_id,
        )

        if self._ingestion_orchestrator is None or self._ingestion_coordinator is None:
            logger.warning(
                "ingestion.phase.skippedmissingdependencies workflow_run_id=%s document_id=%s",
                workflow_run_id,
                workflow.document_id,
            )
            self._workflow_service.update(workflow_run_id, current_step_label="Ingestion dependencies not configured")
            return
        if not self._ingestion_orchestrator.is_configured():
            logger.warning(
                "ingestion.phase.skippednotconfigured workflow_run_id=%s document_id=%s",
                workflow_run_id,
                workflow.document_id,
            )
            self._workflow_service.update(
                workflow_run_id,
                current_step_label="Ingestion skipped (No Azure credentials)",
            )
            return

        self._workflow_service.update(workflow_run_id, current_step_label="Parsing BRD document")
        skipped, result = await self._ingestion_coordinator.run_ingestion_if_needed(
            document.document_id,
            lambda doc: self._run_ingestion_pipeline(workflow_run_id, doc),
        )
        if skipped:
            logger.info(
                "ingestion.phase.skippedalreadyindexed workflow_run_id=%s document_id=%s",
                workflow_run_id,
                workflow.document_id,
            )
            self._workflow_service.update(
                workflow_run_id,
                current_step_label="Ingestion skipped (already indexed)",
            )
            return

        if result is not None:
            logger.info(
                "ingestion.completed workflow_run_id=%s document_id=%s chunk_count=%s page_count=%s embedding_cost_usd=%s",
                workflow_run_id,
                workflow.document_id,
                result.chunk_count,
                result.page_count,
                result.embedding_cost_usd,
            )
            self._apply_ingestion_observability(workflow_run_id, result)
            self._workflow_service.update(
                workflow_run_id,
                current_step_label=f"Ingestion completed ({result.chunk_count} chunks)",
            )

    async def _phase_template_preparation(self, workflow_run_id: str) -> None:
        workflow = self._workflow_service.get_or_raise(workflow_run_id)
        template = self._workflow_service.get_template(workflow.template_id)
        logger.info(
            "templatepreparation.phase.enter workflow_run_id=%s template_id=%s",
            workflow_run_id,
            workflow.template_id,
        )

        if is_inbuilt_template_id(template.template_id):
            doc_type = doc_type_for_inbuilt_template(template.template_id)
            section_plan = get_inbuilt_section_plan(doc_type)
            style_map = get_inbuilt_style_map(doc_type)
            self._workflow_service.update(
                workflow_run_id,
                current_step_label=f"Inbuilt template ready ({doc_type.value})",
                section_plan=[item.model_dump() for item in section_plan],
                style_map=style_map.model_dump(),
                sheet_map={},
            )
            logger.info(
                "templatepreparation.phase.completedinbuilt workflow_run_id=%s template_id=%s doc_type=%s section_count=%s",
                workflow_run_id,
                template.template_id,
                doc_type.value,
                len(section_plan),
            )
            return

        if template.status != TemplateStatus.READY.value:
            raise WorkflowException(f"Template {template.template_id} is not ready: {template.status}")

        section_plan = [SectionDefinition.model_validate(item) for item in (template.section_plan or [])]
        if not section_plan:
            raise WorkflowException(f"Template {template.template_id} has no compiled section plan.")
        style_map = StyleMap.model_validate(template.style_map or {})
        self._workflow_service.update(
            workflow_run_id,
            current_step_label=f"Template ready ({len(section_plan)} sections)",
            section_plan=[item.model_dump() for item in section_plan],
            style_map=style_map.model_dump(),
            sheet_map=template.sheet_map or {},
        )
        logger.info(
            "templatepreparation.phase.completedcustom workflow_run_id=%s template_id=%s section_count=%s",
            workflow_run_id,
            template.template_id,
            len(section_plan),
        )

    async def _phase_section_planning(self, workflow_run_id: str) -> None:
        logger.info("sectionplanning.phase.enter workflow_run_id=%s", workflow_run_id)
        self._workflow_service.update(workflow_run_id, current_step_label="Section planning stub")
        logger.info("sectionplanning.phase.completed workflow_run_id=%s", workflow_run_id)

    async def _phase_retrieval(self, workflow_run_id: str) -> None:
        retrieval_started_at = perf_counter()

        workflow = self._workflow_service.get_or_raise(workflow_run_id)
        section_plan = [SectionDefinition.model_validate(item) for item in (workflow.section_plan or [])]
        logger.info(
            "retrieval.enter workflow_run_id=%s sections=%s max_concurrent=%s",
            workflow_run_id,
            len(section_plan),
            self._max_concurrent_retrieval_sections,
        )

        if not section_plan:
            logger.info("retrieval.phase.skippednosections workflow_run_id=%s", workflow_run_id)
            self._workflow_service.update(workflow_run_id, current_step_label="Retrieval skipped (no sections)")
            return

        if self._section_retriever is None or self._evidence_packager is None:
            message = "Retrieval dependencies not configured"
            if self._is_local_env():
                logger.warning("retrieval.phase.skippedlocalmissingdependencies workflow_run_id=%s", workflow_run_id)
                self._workflow_service.update(workflow_run_id, current_step_label=f"{message} (local skip)")
                return
            raise WorkflowException(message)

        if not self._section_retriever.is_configured():
            message = "Retrieval not configured (missing Azure credentials)"
            if self._is_local_env():
                logger.warning("retrieval.phase.skippedlocalnotconfigured workflow_run_id=%s", workflow_run_id)
                self._workflow_service.update(
                    workflow_run_id,
                    current_step_label=f"{message}; skipped in local env",
                )
                return
            raise WorkflowException(message)

        ordered_sections = sorted(section_plan, key=lambda s: s.execution_order)

        self._workflow_service.update(
            workflow_run_id,
            current_step_label=f"Retrieving evidence for {len(ordered_sections)} sections",
        )

        retrieval_cost_tracker = _RetrievalCostTracker()

        tasks = [
            self._run_retrieval_with_semaphore(
                self._retrieve_one_section(
                    workflow.document_id,
                    section,
                    retrieval_cost_tracker,
                )
            )
            for section in ordered_sections
        ]

        outputs = await asyncio.gather(*tasks)

        logger.info(
            "retrieval.sectiontasks.completed workflow_run_id=%s section_count=%s max_concurrent=%s",
            workflow_run_id,
            len(outputs),
            self._max_concurrent_retrieval_sections,
        )

        section_retrieval_results: dict[str, dict[str, object]] = {}
        total_embedding_cost_usd = 0.0
        total_chunks_retrieved = 0
        zero_hit_sections = 0

        for section_id, bundle_dict, embedding_cost_usd, chunk_count in outputs:
            section_retrieval_results[section_id] = bundle_dict
            total_embedding_cost_usd += embedding_cost_usd
            total_chunks_retrieved += chunk_count
            if chunk_count == 0:
                zero_hit_sections += 1

        updated = self._workflow_service.update(
            workflow_run_id,
            section_retrieval_results=section_retrieval_results,
            current_step_label=f"Retrieved evidence for {len(section_retrieval_results)} sections",
        )

        observability_summary = merge_retrieval_observability(
            getattr(updated, "observability_summary", None),
            llm_cost_usd=retrieval_cost_tracker.llm_cost_usd,
            embedding_cost_usd=total_embedding_cost_usd,
            retrieved_sections=len(section_retrieval_results),
            total_tokens_in=retrieval_cost_tracker.total_tokens_in,
            total_tokens_out=retrieval_cost_tracker.total_tokens_out,
            total_llm_calls=retrieval_cost_tracker.total_llm_calls,
        )

        # Add phase-level retrieval metrics
        observability_summary["retrieval_zero_hit_sections"] = zero_hit_sections
        observability_summary["retrieval_total_chunks"] = total_chunks_retrieved
        observability_summary["retrieval_phase_duration_ms"] = int((perf_counter() - retrieval_started_at) * 1000)
        observability_summary["retrieval_max_concurrent_sections"] = self._max_concurrent_retrieval_sections

        self._workflow_service.update(workflow_run_id, observability_summary=observability_summary)

        logger.info(
            "retrieval.phase.completed workflow_run_id=%s retrieved_sections=%s retrieval_llm_cost_usd=%s "
            "embedding_cost_usd=%s total_chunks=%s zero_hit_sections=%s duration_ms=%s max_concurrent=%s",
            workflow_run_id,
            len(section_retrieval_results),
            retrieval_cost_tracker.llm_cost_usd,
            total_embedding_cost_usd,
            total_chunks_retrieved,
            zero_hit_sections,
            observability_summary["retrieval_phase_duration_ms"],
            self._max_concurrent_retrieval_sections,
        )



    async def _phase_generation(self, workflow_run_id: str) -> None:
        workflow = self._workflow_service.get_or_raise(workflow_run_id)
        section_plan = [SectionDefinition.model_validate(item) for item in (workflow.section_plan or [])]
        logger.info(
            "generation.enter workflow_run_id=%s sections=%s",
            workflow_run_id,
            len(section_plan),
        )
        if not section_plan:
            logger.info("generation.phase.skippednosections workflow_run_id=%s", workflow_run_id)
            self._workflow_service.update(workflow_run_id, current_step_label="Generation skipped (no sections)")
            return

        if self._generation_orchestrator is None:
            message = "Generation dependencies not configured"
            if self._is_local_env():
                logger.warning("generation.phase.skippedlocalmissingdependencies workflow_run_id=%s", workflow_run_id)
                self._workflow_service.update(workflow_run_id, current_step_label=f"{message} (local skip)")
                return
            raise WorkflowException(message)

        if not self._generation_orchestrator.is_configured():
            message = "Generation not configured (missing Azure credentials)"
            if self._is_local_env():
                logger.warning("generation.phase.skippedlocalnotconfigured workflow_run_id=%s", workflow_run_id)
                self._workflow_service.update(
                    workflow_run_id,
                    current_step_label=f"{message}; skipped in local env",
                )
                return
            raise WorkflowException(message)

        self._workflow_service.update(
            workflow_run_id,
            current_step_label=f"Generating content for {len(section_plan)} sections",
        )
        cost_tracker = GenerationCostTracker()

        async def _emit(wid: str, event_type: str, payload: dict[str, object] | None) -> None:
            await self._event_service.emit(wid, event_type, payload)

        raw_results = await self._generation_orchestrator.run_all_sections(
            workflow_run_id=workflow_run_id,
            sections=section_plan,
            section_retrieval_results=dict(workflow.section_retrieval_results or {}),
            doc_type=workflow.doc_type,
            cost_tracker=cost_tracker,
            emit=_emit,
        )
        section_generation_results: dict[str, dict[str, object]] = {}
        for section_id, payload in raw_results.items():
            cleaned = dict(payload)
            cleaned.pop("diagram_source", None)
            section_generation_results[section_id] = GenerationSectionResult.model_validate(cleaned).model_dump()

        failed = sum(1 for row in section_generation_results.values() if row.get("error"))
        completed = len(section_generation_results) - failed
        section_progress = {
            "total": len(section_generation_results),
            "pending": 0,
            "running": 0,
            "completed": completed,
            "failed": failed,
        }

        updated = self._workflow_service.update(
            workflow_run_id,
            section_generation_results=section_generation_results,
            section_progress=section_progress,
            current_step_label=f"Generated {len(section_generation_results)} sections",
        )
        observability_summary = merge_generation_observability(
            getattr(updated, "observability_summary", None),
            llm_cost_usd=cost_tracker.llm_cost_usd,
            generated_sections=len(section_generation_results),
            total_tokens_in=cost_tracker.total_tokens_in,
            total_tokens_out=cost_tracker.total_tokens_out,
            total_llm_calls=cost_tracker.total_llm_calls,
        )
        self._workflow_service.update(workflow_run_id, observability_summary=observability_summary)
        logger.info(
            "generation.phase.completed workflow_run_id=%s completed=%s failed=%s llm_cost_usd=%s total_tokens_in=%s total_tokens_out=%s",
            workflow_run_id,
            completed,
            failed,
            cost_tracker.llm_cost_usd,
            cost_tracker.total_tokens_in,
            cost_tracker.total_tokens_out,
        )

    async def _phase_assembly_validation(self, workflow_run_id: str) -> None:
        workflow = self._workflow_service.get_or_raise(workflow_run_id)
        document = self._workflow_service.get_document(workflow.document_id)
        logger.info(
            "assembly.enter workflow_run_id=%s document_id=%s",
            workflow_run_id,
            workflow.document_id,
        )
        section_plan = [SectionDefinition.model_validate(x) for x in (workflow.section_plan or [])]
        gen = workflow.section_generation_results or {}
        if not section_plan:
            logger.info("assembly.phase.skippednosections workflow_run_id=%s", workflow_run_id)
            self._workflow_service.update(workflow_run_id, current_step_label="Assembly skipped (no sections)")
            return
        outcome = self._document_assembler.assemble(
            document_filename=document.filename,
            doc_type=workflow.doc_type,
            section_plan=section_plan,
            section_generation_results=dict(gen),
        )
        merged_warnings = list(workflow.warnings or []) + outcome.warnings
        self._workflow_service.update(
            workflow_run_id,
            assembled_document=outcome.document.model_dump(),
            warnings=merged_warnings,
            current_step_label=f"Assembled {len(outcome.document.sections)} sections",
        )
        logger.info(
            "assembly.phase.completed workflow_run_id=%s assembled_sections=%s warnings_added=%s",
            workflow_run_id,
            len(outcome.document.sections),
            len(outcome.warnings),
        )

    async def _phase_render_export(self, workflow_run_id: str) -> None:
        if self._output_service is None:
            logger.warning("renderexport.phase.skippednooutputservice workflow_run_id=%s", workflow_run_id)
            self._workflow_service.update(workflow_run_id, current_step_label="Export skipped (no output service)")
            return
        workflow = self._workflow_service.get_or_raise(workflow_run_id)
        logger.info(
            "renderexport.phase.enter workflow_run_id=%s",
            workflow_run_id,
        )
        ad = workflow.assembled_document or {}
        if not ad.get("sections"):
            logger.info("renderexport.phase.skippedemptydocument workflow_run_id=%s", workflow_run_id)
            self._workflow_service.update(workflow_run_id, current_step_label="Export skipped (nothing to render)")
            return

        template = self._workflow_service.get_template(workflow.template_id)
        document = self._workflow_service.get_document(workflow.document_id)
        assembled = AssembledDocument.model_validate(ad)
        style_map = StyleMap.model_validate(workflow.style_map or {})
        out_path, filename, export_warnings = self._export_renderer.render(
            workflow_run_id=workflow_run_id,
            document=ExportDocumentInfo(filename=document.filename),
            template=ExportTemplateInfo(
                template_id=template.template_id,
                template_source=template.template_source,
                file_path=template.file_path,
            ),
            assembled=assembled,
            style_map=style_map,
            sheet_map=dict(workflow.sheet_map or {}),
        )
        wf2 = self._workflow_service.get_or_raise(workflow_run_id)
        render_warnings = list(wf2.warnings or []) + export_warnings
        record = self._output_service.create(
            workflow_run_id=workflow_run_id,
            document_id=document.document_id,
            doc_type=workflow.doc_type,
            file_path=out_path,
            filename=filename,
        )
        self._workflow_service.update(
            workflow_run_id,
            output_id=record.output_id,
            warnings=render_warnings,
            current_step_label="Output file ready",
        )
        await self._event_service.emit(
            workflow_run_id,
            "output.ready",
            {"output_id": record.output_id, "filename": filename},
        )
        logger.info(
            "renderexport.phase.completed workflow_run_id=%s output_id=%s filename=%s warning_count=%s",
            workflow_run_id,
            record.output_id,
            filename,
            len(render_warnings),
        )

    async def _retrieve_one_section(
        self,
        document_id: str,
        section: SectionDefinition,
        cost_tracker: _RetrievalCostTracker,
    ) -> tuple[str, dict[str, object], float, int]:
        if self._section_retriever is None or self._evidence_packager is None:
            raise WorkflowException("Retrieval dependencies not configured.")

        chunks, embedding_cost_usd = await self._section_retriever.retrieve_for_section(
            section,
            document_id=document_id,
            cost_tracker=cost_tracker,
        )

        logger.info(
            "retrieval.section.completed document_id=%s section_id=%s chunk_count=%s embedding_cost_usd=%s",
            document_id,
            section.section_id,
            len(chunks),
            embedding_cost_usd,
        )

        bundle = self._evidence_packager.package(section.section_id, chunks)
        bundle_dict = {
            "context_text": bundle.context_text,
            "citations": [citation.model_dump() for citation in bundle.citations],
        }
        return section.section_id, bundle_dict, embedding_cost_usd, len(chunks)

    async def _run_ingestion_pipeline(
        self,
        workflow_run_id: str,
        document: DocumentRecord,
    ) -> IngestionRunResult:
        self._workflow_service.update(workflow_run_id, current_step_label="Parsing BRD document")
        file_path = Path(settings.documents_path) / document.file_path
        logger.info(
            "ingestion.pipeline.started workflow_run_id=%s document_id=%s file_path=%s content_type=%s",
            workflow_run_id,
            document.document_id,
            file_path,
            document.content_type,
        )
        return await self._ingestion_orchestrator.run(
            workflow_run_id=workflow_run_id,
            document_id=document.document_id,
            file_path=file_path,
            content_type=document.content_type,
        )

    def _apply_ingestion_observability(self, workflow_run_id: str, result: IngestionRunResult) -> None:
        workflow = self._workflow_service.get_or_raise(workflow_run_id)
        merged = merge_full_cost_summary(
            getattr(workflow, "observability_summary", None),
            embedding_cost_usd=result.embedding_cost_usd,
            document_intelligence_cost_usd=result.document_intelligence_cost_usd,
            extra={
                "page_count": result.page_count,
                "indexed_chunk_count": result.chunk_count,
            },
        )
        self._workflow_service.update(workflow_run_id, observability_summary=merged)
        logger.info(
            "ingestion.observability.updated workflow_run_id=%s embedding_cost_usd=%s document_intelligence_cost_usd=%s page_count=%s chunk_count=%s",
            workflow_run_id,
            result.embedding_cost_usd,
            result.document_intelligence_cost_usd,
            result.page_count,
            result.chunk_count,
        )

    async def run(self, workflow_run_id: str) -> None:
        self._workflow_service.get_or_raise(workflow_run_id)
        logger.info("workflow.run.started workflow_run_id=%s", workflow_run_id)
        self._workflow_service.update(
            workflow_run_id,
            status=WorkflowStatus.RUNNING.value,
            started_at=utc_now_iso(),
            current_step_label="Workflow started",
        )
        await self._event_service.emit(workflow_run_id, "workflow.started", {"doc_type": "stub"})

        try:
            await self._run_phase(
                workflow_run_id,
                WorkflowPhase.INPUT_PREPARATION,
                self._phase_input_preparation,
            )
            await self._run_phase(workflow_run_id, WorkflowPhase.INGESTION, self._phase_ingestion)
            await self._run_phase(
                workflow_run_id,
                WorkflowPhase.TEMPLATE_PREPARATION,
                self._phase_template_preparation,
            )
            await self._run_phase(
                workflow_run_id,
                WorkflowPhase.SECTION_PLANNING,
                self._phase_section_planning,
            )
            await self._run_phase(workflow_run_id, WorkflowPhase.RETRIEVAL, self._phase_retrieval)
            await self._run_phase(workflow_run_id, WorkflowPhase.GENERATION, self._phase_generation)
            await self._run_phase(
                workflow_run_id,
                WorkflowPhase.ASSEMBLY_VALIDATION,
                self._phase_assembly_validation,
            )
            await self._run_phase(
                workflow_run_id,
                WorkflowPhase.RENDER_EXPORT,
                self._phase_render_export,
            )

            self._workflow_service.update(
                workflow_run_id,
                status=WorkflowStatus.COMPLETED.value,
                overall_progress_percent=100.0,
                completed_at=utc_now_iso(),
                current_step_label="Workflow completed",
            )
            workflow = self._workflow_service.get_or_raise(workflow_run_id)
            summary = getattr(workflow, "observability_summary", None) or {}
            total_cost = float(summary.get("total_cost_usd", 0.0))
            try:
                await self._event_service.emit(
                    workflow_run_id,
                    "workflow.completed",
                    {"output_id": workflow.output_id, "total_cost_usd": total_cost},
                )
            except Exception:
                logger.exception(
                    "workflow.emit.completedfailed workflow_run_id=%s",
                    workflow_run_id,
                )
            logger.info("workflow.run.completed workflow_run_id=%s", workflow_run_id)
        except Exception as exc:
            logger.exception(
                "workflow.failed workflow_run_id=%s error=%s",
                workflow_run_id,
                str(exc),
            )
            self._workflow_service.update(
                workflow_run_id,
                status=WorkflowStatus.FAILED.value,
                current_step_label=str(exc),
            )
            try:
                await self._event_service.emit(
                    workflow_run_id,
                    "workflow.failed",
                    {"error": str(exc)},
                )
            except Exception:
                logger.exception(
                    "workflow.emit.failedfailed workflow_run_id=%s",
                    workflow_run_id,
                )
            # Do not re-raise: failure is persisted; terminal emit is best-effort for SSE clients.
```

#### `backend/services/workflow_service.py`

**Language hint:** `python`

```python
"""Workflow service for workflow run persistence and guards."""

from __future__ import annotations

from core.constants import DocType, TemplateSource, TemplateStatus, WorkflowStatus
from core.exceptions import ValidationException
from core.ids import utc_now_iso, workflow_id
from modules.template.inbuilt.registry import doc_type_for_inbuilt_template, is_inbuilt_template_id
from repositories.document_models import DocumentRecord
from repositories.document_repo import DocumentRepository
from repositories.template_models import TemplateRecord
from repositories.template_repo import TemplateRepository
from repositories.workflow_models import WorkflowRecord
from repositories.workflow_repo import WorkflowRepository


class WorkflowService:
    def __init__(
        self,
        repo: WorkflowRepository,
        document_repo: DocumentRepository,
        template_repo: TemplateRepository,
    ) -> None:
        self._repo = repo
        self._document_repo = document_repo
        self._template_repo = template_repo

    def create(
        self,
        *,
        document_id: str,
        template_id: str,
        doc_type: str | None = None,
    ) -> WorkflowRecord:
        document = self.get_document(document_id)
        template = self.get_template(template_id)
        resolved_doc_type = doc_type or template.template_type
        if resolved_doc_type is None:
            raise ValidationException("doc_type is required when template has no template_type")

        try:
            normalized_doc_type = DocType(resolved_doc_type).value
        except ValueError as exc:
            raise ValidationException(f"Unsupported doc_type: {resolved_doc_type}") from exc

        if template.template_type and template.template_type != normalized_doc_type:
            raise ValidationException(
                f"Template/doc_type mismatch: template={template.template_type} doc_type={normalized_doc_type}",
            )

        now = utc_now_iso()
        record = WorkflowRecord(
            workflow_run_id=workflow_id(),
            document_id=document.document_id,
            template_id=template.template_id,
            doc_type=normalized_doc_type,
            status=WorkflowStatus.PENDING.value,
            current_phase=None,
            overall_progress_percent=0.0,
            current_step_label="Queued",
            output_id=None,
            created_at=now,
            updated_at=now,
        )
        return self._repo.save(record)

    def get(self, workflow_run_id: str) -> WorkflowRecord | None:
        return self._repo.get(workflow_run_id)

    def get_or_raise(self, workflow_run_id: str) -> WorkflowRecord:
        return self._repo.get_or_raise(workflow_run_id)

    def update(self, workflow_run_id: str, **fields: object) -> WorkflowRecord:
        return self._repo.update(workflow_run_id, **fields)

    def list_all(self) -> list[WorkflowRecord]:
        return self._repo.list_all()

    def get_document(self, document_id: str) -> DocumentRecord:
        return self._document_repo.get_or_raise(document_id)

    def get_template(self, template_id: str) -> TemplateRecord:
        record = self._template_repo.get(template_id)
        if record is not None:
            return record
        if is_inbuilt_template_id(template_id):
            doc_type = doc_type_for_inbuilt_template(template_id).value
            now = utc_now_iso()
            return TemplateRecord(
                template_id=template_id,
                filename=f"{doc_type.lower()}_inbuilt",
                template_type=doc_type,
                template_source=TemplateSource.INBUILT,
                status=TemplateStatus.READY.value,
                compiled_at=now,
                created_at=now,
                updated_at=now,
            )
        return self._template_repo.get_or_raise(template_id)
```

#### `backend/tools/repo_to_markdown.py`

**Language hint:** `python`

```python
#!/usr/bin/env python3
"""
repo_to_markdown.py

Generate a single Markdown file from one or more project directories.
The Markdown includes:
1. Project/folder structure
2. File contents (for code/text files)
3. Nice formatting for LLM context ingestion

Example:
    python repo_to_markdown.py ./backend ./frontend -o project_context.md

Optional:
    python repo_to_markdown.py ./src ./docs -o context.md --max-file-size-kb 512
"""

from __future__ import annotations

import argparse
import fnmatch
import os
from pathlib import Path
from typing import Iterable, List, Set, Tuple
from datetime import datetime


# -------------------------------
# Default configuration
# -------------------------------

DEFAULT_IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".nuxt",
    ".output",
    "coverage",
    ".idea",
    ".vscode",
    "target",
    "bin",
    "obj",
    ".gradle",
    ".DS_Store",
}

DEFAULT_IGNORE_FILES = {
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.so",
    "*.dll",
    "*.exe",
    "*.class",
    "*.jar",
    "*.war",
    "*.zip",
    "*.tar",
    "*.gz",
    "*.7z",
    "*.rar",
    "*.pdf",
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.bmp",
    "*.ico",
    "*.webp",
    "*.mp4",
    "*.mp3",
    "*.wav",
    "*.mov",
    "*.avi",
    "*.mkv",
    "*.woff",
    "*.woff2",
    "*.ttf",
    "*.otf",
    "*.eot",
    "*.lock",
}

# Common code/text extensions that are usually useful for LLM context
DEFAULT_INCLUDE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx",
    ".java", ".kt", ".kts", ".scala",
    ".c", ".h", ".cpp", ".hpp", ".cc", ".hh",
    ".cs",
    ".go",
    ".rs",
    ".php",
    ".rb",
    ".swift",
    ".dart",
    ".lua",
    ".sh", ".bash", ".zsh", ".ps1", ".bat",
    ".sql",
    ".html", ".htm", ".css", ".scss", ".sass", ".less",
    ".xml",
    ".json", ".jsonc",
    ".yaml", ".yml",
    ".toml",
    ".ini", ".cfg", ".conf",
    ".env.example",
    ".md", ".txt", ".rst",
    ".dockerfile",  # some repos use extensionless Dockerfile too
    ".graphql", ".gql",
    ".proto",
}

# Some common extensionless filenames useful for context
DEFAULT_INCLUDE_FILENAMES = {
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "Makefile",
    "README",
    "README.md",
    "README.txt",
    "LICENSE",
    "Procfile",
    ".gitignore",
    ".dockerignore",
    ".editorconfig",
    ".prettierrc",
    ".eslintrc",
    ".npmrc",
    ".nvmrc",
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "Pipfile",
    "Pipfile.lock",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "tsconfig.json",
    "vite.config.ts",
    "vite.config.js",
    "next.config.js",
    "next.config.ts",
    "webpack.config.js",
    "webpack.config.ts",
    "jest.config.js",
    "jest.config.ts",
}


# -------------------------------
# Utility helpers
# -------------------------------

def normalize_extensions(exts: Iterable[str]) -> Set[str]:
    """
    Normalize extensions to start with a dot where applicable.
    Example: 'py' -> '.py'
    """
    normalized = set()
    for ext in exts:
        ext = ext.strip()
        if not ext:
            continue
        if ext.startswith("."):
            normalized.add(ext.lower())
        else:
            normalized.add(f".{ext.lower()}")
    return normalized


def is_binary_file(path: Path, sample_size: int = 4096) -> bool:
    """
    Basic binary detection:
    - If file contains NULL bytes, treat as binary.
    - If decoding as UTF-8 fails badly, treat as binary.
    """
    try:
        with path.open("rb") as f:
            chunk = f.read(sample_size)
        if b"\x00" in chunk:
            return True
        try:
            chunk.decode("utf-8")
            return False
        except UnicodeDecodeError:
            # Could still be text in other encoding, but for LLM context
            # we keep the logic simple and safe.
            return True
    except Exception:
        return True


def should_ignore_file(path: Path, ignore_patterns: Set[str]) -> bool:
    """
    Return True if file name matches any ignored glob pattern.
    """
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(path.name, pattern):
            return True
    return False


def should_include_file(
    path: Path,
    include_extensions: Set[str],
    include_filenames: Set[str],
    ignore_patterns: Set[str],
    max_file_size_kb: int
) -> Tuple[bool, str]:
    """
    Decide whether to include a file in the output.

    Returns:
        (include: bool, reason: str)
    """
    if not path.is_file():
        return False, "Not a file"

    if should_ignore_file(path, ignore_patterns):
        return False, "Ignored by file pattern"

    try:
        size_kb = path.stat().st_size / 1024
        if max_file_size_kb > 0 and size_kb > max_file_size_kb:
            return False, f"Skipped (>{max_file_size_kb} KB)"
    except Exception:
        return False, "Could not read file size"

    if is_binary_file(path):
        return False, "Binary file"

    # Include by explicit filename
    if path.name in include_filenames:
        return True, "Included by filename"

    # Include by extension
    suffixes = path.suffixes
    if suffixes:
        combined_suffix = "".join(suffixes).lower()
        if combined_suffix in include_extensions:
            return True, "Included by combined suffix"

        if path.suffix.lower() in include_extensions:
            return True, "Included by suffix"

    # Special-case extensionless files that are often useful
    if not path.suffix and path.name in include_filenames:
        return True, "Included by extensionless filename"

    return False, "Not a selected code/text file"


def get_markdown_language(path: Path) -> str:
    """
    Map file extension/name to Markdown code fence language.
    """
    name = path.name.lower()
    suffix = path.suffix.lower()

    filename_map = {
        "dockerfile": "dockerfile",
        "makefile": "makefile",
    }
    if name in filename_map:
        return filename_map[name]

    ext_map = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "jsx",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".java": "java",
        ".kt": "kotlin",
        ".kts": "kotlin",
        ".scala": "scala",
        ".c": "c",
        ".h": "c",
        ".cpp": "cpp",
        ".hpp": "cpp",
        ".cc": "cpp",
        ".hh": "cpp",
        ".cs": "csharp",
        ".go": "go",
        ".rs": "rust",
        ".php": "php",
        ".rb": "ruby",
        ".swift": "swift",
        ".dart": "dart",
        ".lua": "lua",
        ".sh": "bash",
        ".bash": "bash",
        ".zsh": "bash",
        ".ps1": "powershell",
        ".bat": "bat",
        ".sql": "sql",
        ".html": "html",
        ".htm": "html",
        ".css": "css",
        ".scss": "scss",
        ".sass": "sass",
        ".less": "less",
        ".xml": "xml",
        ".json": "json",
        ".jsonc": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
        ".ini": "ini",
        ".cfg": "ini",
        ".conf": "conf",
        ".env": "dotenv",
        ".md": "markdown",
        ".txt": "text",
        ".rst": "rst",
        ".graphql": "graphql",
        ".gql": "graphql",
        ".proto": "proto",
    }
    return ext_map.get(suffix, "")


def safe_read_text(path: Path) -> str:
    """
    Read text file safely using UTF-8 first, then fallback.
    """
    encodings = ["utf-8", "utf-8-sig", "latin-1"]
    for encoding in encodings:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except Exception as e:
            return f"[ERROR READING FILE: {e}]"
    return "[ERROR: Unable to decode file as text]"


# -------------------------------
# Tree generation
# -------------------------------

def build_tree(root: Path, ignore_dirs: Set[str], ignore_file_patterns: Set[str], prefix: str = "") -> List[str]:
    """
    Build a simple ASCII tree for a directory.
    """
    lines = []

    try:
        entries = sorted(
            list(root.iterdir()),
            key=lambda p: (not p.is_dir(), p.name.lower())
        )
    except PermissionError:
        return [f"{prefix}[Permission Denied]"]
    except Exception as e:
        return [f"{prefix}[Error: {e}]"]

    # Filter ignored directories and ignored files
    filtered_entries = []
    for entry in entries:
        if entry.is_dir() and entry.name in ignore_dirs:
            continue
        if entry.is_file() and should_ignore_file(entry, ignore_file_patterns):
            continue
        filtered_entries.append(entry)

    for index, entry in enumerate(filtered_entries):
        is_last = index == len(filtered_entries) - 1
        branch = "└── " if is_last else "├── "
        lines.append(f"{prefix}{branch}{entry.name}")

        if entry.is_dir():
            extension = "    " if is_last else "│   "
            lines.extend(build_tree(entry, ignore_dirs, ignore_file_patterns, prefix + extension))

    return lines


# -------------------------------
# File collection
# -------------------------------

def collect_files(
    root: Path,
    ignore_dirs: Set[str],
    ignore_file_patterns: Set[str],
    include_extensions: Set[str],
    include_filenames: Set[str],
    max_file_size_kb: int
) -> List[Path]:
    """
    Recursively collect files that should be included.
    """
    collected: List[Path] = []

    for current_root, dirs, files in os.walk(root):
        current_root_path = Path(current_root)

        # Modify dirs in-place so os.walk skips ignored dirs
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file_name in sorted(files):
            file_path = current_root_path / file_name
            include, _reason = should_include_file(
                file_path,
                include_extensions=include_extensions,
                include_filenames=include_filenames,
                ignore_patterns=ignore_file_patterns,
                max_file_size_kb=max_file_size_kb,
            )
            if include:
                collected.append(file_path)

    collected.sort(key=lambda p: str(p).lower())
    return collected


# -------------------------------
# Markdown generation
# -------------------------------

def generate_markdown(
    roots: List[Path],
    ignore_dirs: Set[str],
    ignore_file_patterns: Set[str],
    include_extensions: Set[str],
    include_filenames: Set[str],
    max_file_size_kb: int,
) -> str:
    """
    Build the final markdown content.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    parts: List[str] = []
    parts.append("# Project Context Export")
    parts.append("")
    parts.append(f"Generated on: `{now}`")
    parts.append("")
    parts.append("## Included Roots")
    parts.append("")
    for root in roots:
        parts.append(f"- `{root.resolve()}`")
    parts.append("")

    # Folder structures
    parts.append("## Folder Structure")
    parts.append("")
    for root in roots:
        parts.append(f"### Root: `{root.name}`")
        parts.append("")
        parts.append("```text")
        parts.append(root.name)
        parts.extend(build_tree(root, ignore_dirs, ignore_file_patterns))
        parts.append("```")
        parts.append("")

    # File contents
    parts.append("## File Contents")
    parts.append("")
    for root in roots:
        files = collect_files(
            root=root,
            ignore_dirs=ignore_dirs,
            ignore_file_patterns=ignore_file_patterns,
            include_extensions=include_extensions,
            include_filenames=include_filenames,
            max_file_size_kb=max_file_size_kb,
        )

        parts.append(f"### Files from `{root.name}`")
        parts.append("")

        if not files:
            parts.append("_No matching code/text files found._")
            parts.append("")
            continue

        for file_path in files:
            relative_path = file_path.relative_to(root)
            language = get_markdown_language(file_path)
            content = safe_read_text(file_path)

            parts.append(f"#### `{root.name}/{relative_path.as_posix()}`")
            parts.append("")
            parts.append(f"**Language hint:** `{language or 'text'}`")
            parts.append("")
            parts.append(f"```{language}")
            parts.append(content.rstrip())
            parts.append("```")
            parts.append("")

    return "\n".join(parts)


# -------------------------------
# CLI
# -------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge multiple project directories into a single LLM-friendly Markdown file."
    )

    parser.add_argument(
        "dirs",
        nargs="+",
        help="One or more directories to scan"
    )

    parser.add_argument(
        "-o",
        "--output",
        default="project_context.md",
        help="Output Markdown file path (default: project_context.md)"
    )

    parser.add_argument(
        "--max-file-size-kb",
        type=int,
        default=512,
        help="Skip files larger than this size in KB (default: 512). Use 0 for no limit."
    )

    parser.add_argument(
        "--ignore-dir",
        action="append",
        default=[],
        help="Additional directory name to ignore. Can be used multiple times."
    )

    parser.add_argument(
        "--ignore-file",
        action="append",
        default=[],
        help="Additional file glob pattern to ignore (example: '*.log'). Can be used multiple times."
    )

    parser.add_argument(
        "--ext",
        action="append",
        default=[],
        help="Additional file extension to include (example: --ext py --ext tsx). Can be used multiple times."
    )

    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden directories/files if they otherwise match filters."
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    roots = [Path(d).resolve() for d in args.dirs]

    for root in roots:
        if not root.exists():
            raise FileNotFoundError(f"Directory does not exist: {root}")
        if not root.is_dir():
            raise NotADirectoryError(f"Not a directory: {root}")

    ignore_dirs = set(DEFAULT_IGNORE_DIRS)
    ignore_dirs.update(args.ignore_dir)

    ignore_file_patterns = set(DEFAULT_IGNORE_FILES)
    ignore_file_patterns.update(args.ignore_file)

    include_extensions = set(DEFAULT_INCLUDE_EXTENSIONS)
    include_extensions.update(normalize_extensions(args.ext))

    include_filenames = set(DEFAULT_INCLUDE_FILENAMES)

    # If hidden files/dirs are not included, ignore dot-directories except specific useful files.
    if not args.include_hidden:
        # We avoid globally ignoring dot-files here because some are useful,
        # but hidden directories are already mostly covered.
        pass

    markdown = generate_markdown(
        roots=roots,
        ignore_dirs=ignore_dirs,
        ignore_file_patterns=ignore_file_patterns,
        include_extensions=include_extensions,
        include_filenames=include_filenames,
        max_file_size_kb=args.max_file_size_kb,
    )

    output_path = Path(args.output).resolve()
    output_path.write_text(markdown, encoding="utf-8")

    print(f"Markdown context file created successfully: {output_path}")


if __name__ == "__main__":
    main()
```

#### `backend/tools/smoke_azure.py`

**Language hint:** `python`

```python
from __future__ import annotations

import os
import sys
import requests
from dotenv import load_dotenv
load_dotenv()

SEARCH_API_VERSION = "2025-09-01"
OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")


def fail(msg: str, code: int = 1) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(code)


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def info(msg: str) -> None:
    print(f"[INFO] {msg}")


def smoke_ai_search() -> None:
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT", "").rstrip("/")
    api_key = os.getenv("AZURE_SEARCH_API_KEY", "")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "").strip()

    if not endpoint:
        fail("Missing AZURE_SEARCH_ENDPOINT")
    if not api_key:
        fail("Missing AZURE_SEARCH_API_KEY")

    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
    }

    # 1) Basic connectivity + auth check: list indexes
    list_indexes_url = f"{endpoint}/indexes?api-version={SEARCH_API_VERSION}"
    try:
        r = requests.get(list_indexes_url, headers=headers, timeout=20)
    except requests.RequestException as exc:
        fail(f"Could not connect to Azure AI Search: {exc}")

    if r.status_code == 401:
        fail("Azure AI Search unauthorized: API key is invalid or missing.")
    if r.status_code == 403:
        fail("Azure AI Search forbidden: key does not have required permissions.")
    if r.status_code != 200:
        fail(f"Unexpected status while listing indexes: {r.status_code} | {r.text[:500]}")

    ok("Azure AI Search service is reachable and authentication is working.")

    body = r.json()
    indexes = body.get("value", [])
    ok(f"List indexes call succeeded. Index count: {len(indexes)}")

    if indexes:
        info("Indexes available in the service:")
        for idx, item in enumerate(indexes, start=1):
            name = item.get("name", "<unknown>")
            print(f"   {idx}. {name}")
    else:
        info("No indexes found in the service.")

    # 2) Optional: index-specific smoke test
    if index_name:
        stats_url = f"{endpoint}/indexes('{index_name}')/search.stats?api-version={SEARCH_API_VERSION}"
        r2 = requests.get(stats_url, headers=headers, timeout=20)

        if r2.status_code == 404:
            fail(f"Index '{index_name}' does not exist.")
        if r2.status_code == 401:
            fail("Azure AI Search unauthorized when fetching index stats.")
        if r2.status_code == 403:
            fail("Azure AI Search forbidden when fetching index stats.")
        if r2.status_code != 200:
            fail(f"Failed to fetch stats for index '{index_name}': {r2.status_code} | {r2.text[:500]}")

        stats = r2.json()
        ok(
            "Index statistics retrieved successfully: "
            f"documentCount={stats.get('documentCount')}, "
            f"storageSize={stats.get('storageSize')}, "
            f"vectorIndexSize={stats.get('vectorIndexSize')}"
        )


def smoke_azure_openai() -> None:
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
    deployment = os.getenv("AZURE_OPENAI_GPT5_DEPLOYMENT", "").strip()

    if not endpoint:
        fail("Missing AZURE_OPENAI_ENDPOINT")
    if not api_key:
        fail("Missing AZURE_OPENAI_API_KEY")
    if not deployment:
        fail("Missing AZURE_OPENAI_DEPLOYMENT_NAME")

    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
    }

    url = (
        f"{endpoint}/openai/deployments/{deployment}/chat/completions"
        f"?api-version={OPENAI_API_VERSION}"
    )

    payload = {
        "messages": [
            {"role": "system", "content": "You are a smoke test assistant."},
            {"role": "user", "content": "Reply with exactly: Azure OpenAI smoke test passed."},
        ],
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
    except requests.RequestException as exc:
        fail(f"Could not connect to Azure OpenAI: {exc}")

    if r.status_code == 401:
        fail("Azure OpenAI unauthorized: API key is invalid or missing.")
    if r.status_code == 403:
        fail("Azure OpenAI forbidden: key does not have required permissions.")
    if r.status_code == 404:
        fail("Azure OpenAI deployment or endpoint not found.")
    if r.status_code != 200:
        fail(f"Azure OpenAI smoke test failed: {r.status_code} | {r.text[:1000]}")

    body = r.json()
    choices = body.get("choices") or []
    if not choices:
        fail("Azure OpenAI returned 200 OK but no choices were present in the response.")

    message = choices[0].get("message", {})
    content = message.get("content", "")

    ok("Azure OpenAI endpoint is reachable and chat completion succeeded.")
    info(f"Azure OpenAI response preview: {str(content)[:200]}")


def main() -> None:
    print("=== Azure AI Search Smoke Test ===")
    smoke_ai_search()

    print("\n=== Azure OpenAI Smoke Test ===")
    smoke_azure_openai()

    print("\nSmoke test completed successfully.")


if __name__ == "__main__":
    main()
```

#### `backend/workers/__init__.py`

**Language hint:** `python`

```python
"""Worker utilities."""
```

#### `backend/workers/dispatcher.py`

**Language hint:** `python`

```python
"""Background task dispatcher used by API dependencies."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import BackgroundTasks

from core.logging import get_logger, verbose_logs_enabled

logger = get_logger(__name__)


async def _run_guarded(
    fn: Callable[..., Awaitable[Any]],
    args: tuple[Any, ...],
) -> None:
    if verbose_logs_enabled():
        logger.info("backgroundtask.run.started task=%s args_count=%s", getattr(fn, "__name__", str(fn)), len(args))
    try:
        await fn(*args)
        if verbose_logs_enabled():
            logger.info("backgroundtask.run.completed task=%s", getattr(fn, "__name__", str(fn)))
    except Exception:
        resource_id: str | None = None
        if len(args) == 1 and isinstance(args[0], str):
            resource_id = args[0]
        logger.exception(
            "backgroundtask.run.failed legacy=background_task_failed task=%s resource_id=%s",
            getattr(fn, "__name__", str(fn)),
            resource_id,
        )


class TaskDispatcher:
    def dispatch(
        self,
        background_tasks: BackgroundTasks | None,
        fn: Callable[..., Awaitable[Any]],
        *args: Any,
    ) -> None:
        bound = (fn, tuple(args))

        if background_tasks is not None:
            if verbose_logs_enabled():
                logger.info("backgroundtask.dispatch.started mode=fastapi task=%s", getattr(fn, "__name__", str(fn)))
            background_tasks.add_task(_run_guarded, bound[0], bound[1])
            return

        try:
            if verbose_logs_enabled():
                logger.info("backgroundtask.dispatch.started mode=asyncio task=%s", getattr(fn, "__name__", str(fn)))
            asyncio.get_running_loop().create_task(_run_guarded(bound[0], bound[1]))
        except RuntimeError:
            logger.exception("backgroundtask.dispatch.failed reason=no_running_event_loop")
```