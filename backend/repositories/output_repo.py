"""Output repository — persists :class:`OutputRecord` as JSON files."""

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
