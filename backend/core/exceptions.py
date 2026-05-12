"""Domain exception hierarchy for the AI SDLC backend.

Every error raised from business code should be a subclass of
:class:`SDLCBaseException`. The :mod:`main` module installs FastAPI exception
handlers that translate these classes into the standard JSON envelope from
:mod:`core.response`:

- ``NotFoundException``      -> ``404 Not Found``
- any other ``SDLCBaseException`` -> ``400 Bad Request``
- bare ``Exception``         -> ``500 Internal Server Error``

The ``code`` attribute is a stable machine-readable identifier consumed by
the frontend and by tests. Treat it as part of the public API: do not rename
codes without coordinating with the UI.
"""

from __future__ import annotations


class SDLCBaseException(Exception):
    """Root of the domain exception tree.

    Attributes
    ----------
    message:
        Human-readable description suitable for surfacing to API consumers.
    code:
        Stable machine identifier (e.g. ``WORKFLOW_ERROR``). Frontend code
        branches on this value.
    """

    def __init__(self, message: str, code: str = "SDLC_ERROR") -> None:
        self.message = message
        self.code = code
        # Pass ``message`` to ``Exception`` so the default ``str(exc)`` is
        # useful in logs and Python tracebacks.
        super().__init__(message)


class ValidationException(SDLCBaseException):
    """Raised when caller input fails validation (shape, ranges, enums)."""

    def __init__(self, message: str, code: str = "VALIDATION_ERROR") -> None:
        super().__init__(message, code)


class NotFoundException(SDLCBaseException):
    """Raised when a resource lookup by ID fails.

    Carries the ``resource`` (kind, e.g. ``"document"``) and ``resource_id``
    separately so observers can build links or precise error messages without
    string-parsing.
    """

    def __init__(self, resource: str, resource_id: str, code: str = "NOT_FOUND") -> None:
        self.resource = resource
        self.resource_id = resource_id
        super().__init__(f"{resource} not found: {resource_id}", code)


class WorkflowException(SDLCBaseException):
    """Raised by orchestration code in ``services.workflow_executor`` / ``modules``."""

    def __init__(self, message: str, code: str = "WORKFLOW_ERROR") -> None:
        super().__init__(message, code)


class IngestionException(SDLCBaseException):
    """Raised by parsing/chunking/indexing failures in ``modules.ingestion``."""

    def __init__(self, message: str, code: str = "INGESTION_ERROR") -> None:
        super().__init__(message, code)


class TemplateException(SDLCBaseException):
    """Raised by template extraction, normalization, or validation."""

    def __init__(self, message: str, code: str = "TEMPLATE_ERROR") -> None:
        super().__init__(message, code)


class GenerationException(SDLCBaseException):
    """Raised when an LLM call or generation orchestration step fails."""

    def __init__(self, message: str, code: str = "GENERATION_ERROR") -> None:
        super().__init__(message, code)


class ExportException(SDLCBaseException):
    """Raised by DOCX/XLSX export and post-render integrity checks."""

    def __init__(self, message: str, code: str = "EXPORT_ERROR") -> None:
        super().__init__(message, code)
