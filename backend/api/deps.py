"""Dependency providers for API routes."""

from __future__ import annotations

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


def get_workflow_executor() -> WorkflowExecutor:
    return WorkflowExecutor(
        workflow_service=get_workflow_service(),
        event_service=get_event_service(),
    )
