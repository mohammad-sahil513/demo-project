"""Evidence packaging for section-level retrieval results.

Takes the list of :class:`RetrievedChunk` produced by
:class:`SectionRetriever` and turns it into an :class:`EvidenceBundle`:

- ``context_text`` — every chunk rendered as ``[Source N - heading, p.X (type)]``
  followed by the chunk body. The numbered, labeled prefix is what generation
  prompts ask the model to cite by reference.
- ``citations``   — a structured list mirroring the same chunks so the
  frontend can render clickable citation badges.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Citation(BaseModel):
    """One citation source attached to an :class:`EvidenceBundle`."""

    model_config = ConfigDict(extra="ignore")

    path: str
    page: int | None = None
    content_type: str = "text"
    chunk_id: str


class EvidenceBundle(BaseModel):
    """All evidence for one section — fed into the generation prompt."""

    model_config = ConfigDict(extra="ignore")

    section_id: str
    context_text: str = ""
    citations: list[Citation] = Field(default_factory=list)


class EvidencePackager:
    """Convert retrieved chunks into generator-ready evidence bundles."""

    def package(self, section_id: str, chunks: list[object]) -> EvidenceBundle:
        """Render ``chunks`` into the prompt-friendly source block format."""
        citations: list[Citation] = []
        source_blocks: list[str] = []

        for index, chunk in enumerate(chunks, start=1):
            # Use ``getattr`` so we accept any object shape (e.g. SearchChunk,
            # a plain dict-shaped namespace, or a future RetrievedChunk
            # variant) — only ``chunk_id``/``text`` are strictly required.
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

            # ``p.?`` is used when Document Intelligence didn't return a
            # page number — better than dropping the source entirely.
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
