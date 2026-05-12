"""Dependency providers for API routes — FastAPI ``Depends(...)`` wiring.

Every service the API needs is constructed here and injected into routes
via FastAPI's dependency system. This single module is therefore the
composition root for the request-handling side of the backend.

Two patterns are used:

- ``@lru_cache(maxsize=1)`` for adapter and module-level singletons that
  hold expensive resources (HTTP clients, encoders) or rely on caches.
- Plain factory functions for services and repositories — they are
  cheap to construct per request and keep state on the underlying
  repository, not on the service itself.

Two true module-level singletons live at the top of the file:

- :data:`event_service_singleton`   the in-memory SSE broker; sharing
                                    state across requests is the whole
                                    point.
- :data:`task_dispatcher_singleton` background task helper; stateless,
                                    so a single instance is sufficient.
"""

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
