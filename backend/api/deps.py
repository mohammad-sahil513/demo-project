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
    return TemplateService(get_template_repository())


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
    return DocumentChunker()


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


def get_workflow_executor() -> WorkflowExecutor:
    return WorkflowExecutor(
        workflow_service=get_workflow_service(),
        event_service=get_event_service(),
        ingestion_orchestrator=get_ingestion_orchestrator(),
        ingestion_coordinator=get_ingestion_coordinator(),
    )
