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
