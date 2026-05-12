"""Document repository — persists :class:`DocumentRecord` as JSON files.

Methods are thin wrappers around :class:`BaseJsonRepository` that pin the
resource name (used in 404 messages) and the primary key field.
"""

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
        """Return the record or raise ``NotFoundException("Document", ...)``."""
        return super().get_or_raise(document_id, resource_name)

    def update(self, document_id: str, **fields: object) -> DocumentRecord:
        """Partial update with ``Document`` resource label for error messages."""
        return super().update(document_id, resource_name="Document", **fields)
