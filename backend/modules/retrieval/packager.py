"""Evidence packaging for section-level retrieval results."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Citation(BaseModel):
    model_config = ConfigDict(extra="ignore")

    path: str
    page: int | None = None
    content_type: str = "text"
    chunk_id: str


class EvidenceBundle(BaseModel):
    model_config = ConfigDict(extra="ignore")

    section_id: str
    context_text: str = ""
    citations: list[Citation] = Field(default_factory=list)


class EvidencePackager:
    """Convert retrieved chunks into generator-ready evidence bundles."""

    def package(self, section_id: str, chunks: list[object]) -> EvidenceBundle:
        citations: list[Citation] = []
        source_blocks: list[str] = []

        for index, chunk in enumerate(chunks, start=1):
            chunk_id = str(getattr(chunk, "chunk_id", "") or "")
            text = str(getattr(chunk, "text", "") or "")
            path = str(getattr(chunk, "section_heading", "") or "Document")
            page = self._to_optional_int(getattr(chunk, "page_number", None))
            content_type = str(getattr(chunk, "content_type", "") or "text")

            citations.append(
                Citation(
                    path=path,
                    page=page,
                    content_type=content_type,
                    chunk_id=chunk_id,
                ),
            )

            page_label = f"p.{page}" if page is not None else "p.?"
            source_blocks.append(
                f"[Source {index} - {path}, {page_label} ({content_type})]\n{text}",
            )

        context_text = "\n\n---\n\n".join(source_blocks)
        return EvidenceBundle(section_id=section_id, context_text=context_text, citations=citations)

    @staticmethod
    def _to_optional_int(value: object) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
