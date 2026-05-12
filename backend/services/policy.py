"""Cross-cutting validation rules shared across services and API routes.

Small, dependency-free guard functions that raise
:class:`ValidationException` when an invariant is violated. Pulling these
into a separate module keeps the rules unit-testable and ensures both the
API layer (pre-validation) and the workflow service (defense in depth)
enforce the same checks.
"""

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
