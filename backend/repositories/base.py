"""Generic JSON file repository."""

from __future__ import annotations

from pathlib import Path
from typing import Generic, TypeVar

import orjson
from pydantic import BaseModel

from core.exceptions import NotFoundException
from core.ids import utc_now_iso
from core.logging import get_logger

T = TypeVar("T", bound=BaseModel)
logger = get_logger(__name__)


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
        logger.info(
            "repository.save model=%s id=%s path=%s",
            self._model_class.__name__,
            record_id,
            self._file(record_id),
        )
        self._file(record_id).write_bytes(orjson.dumps(payload, option=orjson.OPT_INDENT_2))
        return record

    def get(self, record_id: str) -> T | None:
        file_path = self._file(record_id)
        if not file_path.is_file():
            logger.info(
                "repository.get.miss model=%s id=%s path=%s",
                self._model_class.__name__,
                record_id,
                file_path,
            )
            return None
        logger.info(
            "repository.get.hit model=%s id=%s path=%s",
            self._model_class.__name__,
            record_id,
            file_path,
        )
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
        logger.info(
            "repository.list_all model=%s path=%s total=%s",
            self._model_class.__name__,
            self._path,
            len(records),
        )
        return records

    def update(self, record_id: str, resource_name: str, **fields: object) -> T:
        logger.info(
            "repository.update.started model=%s id=%s fields=%s",
            self._model_class.__name__,
            record_id,
            sorted(fields.keys()),
        )
        record = self.get_or_raise(record_id, resource_name)
        current = record.model_dump()
        current.update(fields)
        if "updated_at" in current:
            current["updated_at"] = utc_now_iso()
        updated = self._model_class.model_validate(current)
        self.save(updated)
        logger.info(
            "repository.update.completed model=%s id=%s",
            self._model_class.__name__,
            record_id,
        )
        return updated

    def delete(self, record_id: str) -> bool:
        file_path = self._file(record_id)
        if not file_path.is_file():
            logger.info(
                "repository.delete.miss model=%s id=%s path=%s",
                self._model_class.__name__,
                record_id,
                file_path,
            )
            return False
        file_path.unlink()
        logger.info(
            "repository.delete.completed model=%s id=%s path=%s",
            self._model_class.__name__,
            record_id,
            file_path,
        )
        return True
