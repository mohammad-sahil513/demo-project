"""Output service — manage final exported artifact records.

A new :class:`OutputRecord` is created once the RENDER_EXPORT phase
writes the final DOCX/XLSX file to disk. The record is the only entity
the frontend needs to construct a download URL; the actual binary lives
under ``storage/outputs/``.

``get_download_info`` returns the absolute path and filename; the API
streams the bytes via :class:`fastapi.responses.FileResponse`.
"""

from __future__ import annotations

from pathlib import Path

from core.ids import output_id, utc_now_iso
from core.constants import OutputFormat
from core.exceptions import ValidationException
from repositories.output_models import OutputRecord
from repositories.output_repo import OutputRepository


class OutputService:
    def __init__(self, repo: OutputRepository) -> None:
        self._repo = repo

    def create(
        self,
        *,
        workflow_run_id: str,
        document_id: str,
        doc_type: str,
        file_path: Path,
        filename: str,
    ) -> OutputRecord:
        extension = file_path.suffix.lower()
        if extension == ".docx":
            output_format = OutputFormat.DOCX.value
        elif extension == ".xlsx":
            output_format = OutputFormat.XLSX.value
        else:
            raise ValidationException(f"Unsupported output extension: {extension}")

        now = utc_now_iso()
        record = OutputRecord(
            output_id=output_id(),
            workflow_run_id=workflow_run_id,
            document_id=document_id,
            doc_type=doc_type,
            output_format=output_format,
            status="READY",
            file_path=str(file_path),
            filename=filename,
            size_bytes=file_path.stat().st_size if file_path.exists() else 0,
            created_at=now,
            updated_at=now,
            ready_at=now,
        )
        return self._repo.save(record)

    def get_or_raise(self, output_id_value: str) -> OutputRecord:
        return self._repo.get_or_raise(output_id_value)

    def get_download_info(self, output_id_value: str) -> tuple[Path, str]:
        record = self.get_or_raise(output_id_value)
        path = Path(record.file_path)
        if not path.exists():
            raise ValidationException(f"Output file does not exist for {output_id_value}")
        return path, record.filename
