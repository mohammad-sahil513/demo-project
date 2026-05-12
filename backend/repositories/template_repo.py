"""Template repository — persists :class:`TemplateRecord` as JSON files.

Thin wrapper over :class:`BaseJsonRepository` that pins the primary key and
the human-facing resource name used for 404 messages.
"""

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
