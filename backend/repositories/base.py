"""Generic JSON file repository."""

from __future__ import annotations

from pathlib import Path
from typing import Generic, TypeVar

import orjson
from pydantic import BaseModel

from core.exceptions import NotFoundException
from core.ids import utc_now_iso

T = TypeVar("T", bound=BaseModel)


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
        self._file(record_id).write_bytes(orjson.dumps(payload, option=orjson.OPT_INDENT_2))
        return record

    def get(self, record_id: str) -> T | None:
        file_path = self._file(record_id)
        if not file_path.is_file():
            return None
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
        return records

    def update(self, record_id: str, resource_name: str, **fields: object) -> T:
        record = self.get_or_raise(record_id, resource_name)
        current = record.model_dump()
        current.update(fields)
        if "updated_at" in current:
            current["updated_at"] = utc_now_iso()
        updated = self._model_class.model_validate(current)
        self.save(updated)
        return updated

    def delete(self, record_id: str) -> bool:
        file_path = self._file(record_id)
        if not file_path.is_file():
            return False
        file_path.unlink()
        return True
