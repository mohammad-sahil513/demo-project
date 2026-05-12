"""Generic JSON-file repository with CRUD + list operations.

Every concrete repository (documents, templates, workflows, outputs) inherits
from :class:`BaseJsonRepository` and supplies:

- the Pydantic ``model_class`` for serialization/validation
- ``_id_field`` — the attribute name that holds the unique ID
- optional ``get_or_raise`` and ``update`` overrides that pin a resource name
  for nicer 404 messages

Storage format
--------------
Each record is one pretty-printed JSON file named ``<id>.json`` under the
repo's ``storage_path``. Writes use ``orjson`` (with ``OPT_INDENT_2``) for
speed; reads use ``orjson.loads`` and Pydantic ``model_validate`` for
defense-in-depth validation against schema drift.

Concurrency
-----------
The current single-process FastAPI deployment means we can rely on the OS
to atomically rename within a single mount — a multi-writer deployment would
need to add file locking here.
"""

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
    """Reusable CRUD over a directory of ``<id>.json`` files."""

    def __init__(self, storage_path: Path, model_class: type[T]) -> None:
        self._path = storage_path
        self._model_class = model_class
        # Idempotent — also makes tests easier (no need to pre-create dirs).
        self._path.mkdir(parents=True, exist_ok=True)

    def _id_field(self) -> str:
        """Subclasses return the attribute name that holds the primary key."""
        raise NotImplementedError

    def _file(self, record_id: str) -> Path:
        """Compute the on-disk path for ``record_id``."""
        return self._path / f"{record_id}.json"

    def save(self, record: T) -> T:
        """Serialize and overwrite the record file.

        ``OPT_INDENT_2`` keeps the file human-readable — useful when
        debugging from a checked-out storage volume.
        """
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
        """Return the record or ``None`` if no file exists.

        Pydantic ``model_validate`` will raise on malformed JSON / wrong shape
        — let that propagate; corrupt records should surface, not be hidden.
        """
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
        """``get`` but raises :class:`NotFoundException` when missing.

        The ``resource_name`` is what surfaces in the API error payload —
        e.g. ``"Document not found: doc-…"``.
        """
        record = self.get(record_id)
        if record is None:
            raise NotFoundException(resource_name, record_id)
        return record

    def list_all(self) -> list[T]:
        """Return every record in this repository, newest first.

        Sorting is keyed on ``created_at`` (string ISO-8601), which is fine
        because ISO-8601 timestamps sort lexicographically the same as
        chronologically. Records without ``created_at`` fall to the end.
        """
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
        """Partial update — read, merge ``fields``, re-validate, save.

        Always bumps ``updated_at`` to the current UTC time so observers can
        detect changes by mtime alone (used by the SSE event stream).
        """
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
        # Re-validate via the Pydantic model so a buggy caller cannot persist
        # garbage values (wrong types, missing required fields).
        updated = self._model_class.model_validate(current)
        self.save(updated)
        logger.info(
            "repository.update.completed model=%s id=%s",
            self._model_class.__name__,
            record_id,
        )
        return updated

    def delete(self, record_id: str) -> bool:
        """Remove the record's file. Returns ``True`` if anything was deleted."""
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
