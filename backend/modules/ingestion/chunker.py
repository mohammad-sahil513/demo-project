"""Hybrid chunking for parsed BRD documents."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from core.ids import chunk_id_for_document
from infrastructure.doc_intelligence import ParsedDocument

_HEADING_RE = re.compile(
    r"(?m)^(#{1,6}\s+.+|[A-Z][A-Z0-9\s\-]{4,}|(?:\d+(?:\.\d+)*)\s+[^\n]+)\s*$",
)
_TOKEN_RE = re.compile(r"\S+")


@dataclass(slots=True, frozen=True)
class IngestionChunk:
    chunk_id: str
    document_id: str
    workflow_run_id: str
    text: str
    chunk_index: int
    section_heading: str | None
    page_number: int | None
    content_type: str


class DocumentChunker:
    """Split parsed content into table and text chunks."""

    def __init__(self, *, chunk_size: int = 512, overlap: int = 64) -> None:
        self._chunk_size = max(32, chunk_size)
        self._overlap = max(0, min(overlap, self._chunk_size - 1))

    def chunk(
        self,
        *,
        document_id: str,
        workflow_run_id: str,
        parsed: ParsedDocument,
    ) -> list[IngestionChunk]:
        chunks: list[IngestionChunk] = []
        chunk_index = 0
        page_markers = self._page_markers(parsed.raw_result)

        for table in parsed.tables:
            text = table.markdown.strip()
            if not text:
                continue
            chunks.append(
                IngestionChunk(
                    chunk_id=chunk_id_for_document(document_id, chunk_index),
                    document_id=document_id,
                    workflow_run_id=workflow_run_id,
                    text=text,
                    chunk_index=chunk_index,
                    section_heading="Table",
                    page_number=table.page_number,
                    content_type="table",
                ),
            )
            chunk_index += 1

        for heading, body, start_offset in self._split_sections(parsed.full_text):
            page_number = self._resolve_page_from_offset(start_offset, page_markers)
            for text_piece in self._sliding_windows(body):
                if self._token_count(text_piece) < 10:
                    continue
                chunks.append(
                    IngestionChunk(
                        chunk_id=chunk_id_for_document(document_id, chunk_index),
                        document_id=document_id,
                        workflow_run_id=workflow_run_id,
                        text=text_piece,
                        chunk_index=chunk_index,
                        section_heading=heading,
                        page_number=page_number,
                        content_type="text",
                    ),
                )
                chunk_index += 1

        return chunks

    def _split_sections(self, text: str) -> list[tuple[str | None, str, int]]:
        original = text
        text = text.strip()
        if not text:
            return []

        matches = list(_HEADING_RE.finditer(text))
        if not matches:
            return [(None, text, max(0, original.find(text)))]

        sections: list[tuple[str | None, str, int]] = []
        cursor = 0
        for index, match in enumerate(matches):
            heading = match.group(0).strip()
            start = match.end()
            if match.start() > cursor:
                preface = text[cursor : match.start()].strip()
                if preface:
                    sections.append((None, preface, max(0, original.find(preface))))
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            if body:
                sections.append((heading, body, max(0, original.find(body))))
            cursor = end
        if not sections:
            sections.append((None, text, max(0, original.find(text))))
        return sections

    def _sliding_windows(self, text: str) -> list[str]:
        tokens = _TOKEN_RE.findall(text)
        if not tokens:
            return []
        if len(tokens) <= self._chunk_size:
            return [" ".join(tokens)]

        out: list[str] = []
        step = max(1, self._chunk_size - self._overlap)
        for start in range(0, len(tokens), step):
            window = tokens[start : start + self._chunk_size]
            if not window:
                break
            out.append(" ".join(window))
            if start + self._chunk_size >= len(tokens):
                break
        return out

    def _token_count(self, text: str) -> int:
        return len(_TOKEN_RE.findall(text))

    def _page_markers(self, raw_result: dict[str, Any]) -> list[tuple[int, int]]:
        markers: list[tuple[int, int]] = []
        paragraphs = raw_result.get("paragraphs") if isinstance(raw_result, dict) else None
        if not isinstance(paragraphs, list):
            return markers

        for paragraph in paragraphs:
            if not isinstance(paragraph, dict):
                continue
            spans = paragraph.get("spans")
            regions = paragraph.get("boundingRegions")
            if not isinstance(spans, list) or not spans:
                continue
            if not isinstance(regions, list) or not regions:
                continue
            first_span = spans[0]
            first_region = regions[0]
            if not isinstance(first_span, dict) or not isinstance(first_region, dict):
                continue
            offset = first_span.get("offset")
            page = first_region.get("pageNumber")
            if isinstance(offset, int) and isinstance(page, int):
                markers.append((offset, page))

        markers.sort(key=lambda item: item[0])
        return markers

    def _resolve_page_from_offset(self, offset: int, markers: list[tuple[int, int]]) -> int | None:
        if not markers:
            return None
        page: int | None = None
        for marker_offset, marker_page in markers:
            if marker_offset <= offset:
                page = marker_page
            else:
                break
        return page if page is not None else markers[0][1]
