"""LLM markdown table generation.

Sections marked ``output_type="table"`` are emitted by the LLM as a GFM
markdown pipe table. The model occasionally:

- wraps the table in decorative markdown (``**_| ... |_**``),
- skips the ``| --- | --- |`` separator row,
- emits trailing prose after the table.

This module's :func:`_normalize_markdown_table` strips wrappers, ensures
the separator row exists, and discards any non-table lines that follow.
The export DOCX/XLSX builders parse the cleaned GFM markdown.
"""
from __future__ import annotations

import re
from typing import Any

from core.constants import TASK_TO_MODEL
from infrastructure.sk_adapter import AzureSKAdapter
from modules.generation.context import build_prompt_mapping, evidence_text_from_retrieval
from modules.generation.cost_tracking import GenerationCostTracker, llm_delta_between_snapshots
from modules.generation.prompt_loader import GenerationPromptLoader
from modules.template.models import SectionDefinition


_TABLE_LINE_RE = re.compile(r"^\s*\|.+\|\s*$")
_SEPARATOR_CELL_RE = re.compile(r"^\s*:?-{3,}:?\s*$")


def _unwrap_table_line(line: str) -> str:
    """
    Remove decorative wrappers that sometimes surround model output lines,
    for example **_| a | b |_**.
    """
    stripped = line.strip()

    wrappers = [
        ("**_", "_**"),
        ("**", "**"),
        ("__", "__"),
        ("_", "_"),
    ]
    for prefix, suffix in wrappers:
        if stripped.startswith(prefix) and stripped.endswith(suffix) and len(stripped) > len(prefix) + len(suffix):
            inner = stripped[len(prefix):-len(suffix)].strip()
            if "|" in inner:
                return inner
    return stripped


def _split_pipe_cells(line: str) -> list[str]:
    body = line.strip().strip("|")
    return [cell.strip() for cell in body.split("|")]


def _is_separator_row(line: str) -> bool:
    cells = _split_pipe_cells(_unwrap_table_line(line))
    if not cells:
        return False
    return all(_SEPARATOR_CELL_RE.match(cell) is not None for cell in cells)


def _extract_first_table_lines(text: str) -> list[str]:
    """
    Return the first contiguous pipe-table block found in the model output.
    """
    lines = text.splitlines()
    table_lines: list[str] = []
    collecting = False

    for raw in lines:
        line = _unwrap_table_line(raw)
        if _TABLE_LINE_RE.match(line):
            table_lines.append(line)
            collecting = True
            continue

        if collecting:
            break

    return table_lines


def _normalize_markdown_table(text: str) -> str:
    """
    Normalize the first detected markdown pipe table into a clean GFM table:
    - header row
    - separator row
    - normalized pipe formatting

    If no table block is found, return the original stripped text.
    """
    table_lines = _extract_first_table_lines(text)
    if len(table_lines) < 2:
        return text.strip()

    header_cells = _split_pipe_cells(table_lines[0])
    if not header_cells:
        return text.strip()

    body_lines = table_lines[1:]

    normalized: list[str] = []
    normalized.append("| " + " | ".join(header_cells) + " |")

    if body_lines and _is_separator_row(body_lines[0]):
        normalized.append("| " + " | ".join("---" for _ in header_cells) + " |")
        data_lines = body_lines[1:]
    else:
        normalized.append("| " + " | ".join("---" for _ in header_cells) + " |")
        data_lines = body_lines

    for line in data_lines:
        clean = _unwrap_table_line(line)
        if not _TABLE_LINE_RE.match(clean):
            continue
        normalized.append("| " + " | ".join(_split_pipe_cells(clean)) + " |")

    return "\n".join(normalized).strip()


class TableSectionGenerator:
    """Generates GFM markdown tables for ``output_type="table"`` sections."""

    def __init__(self, sk_adapter: AzureSKAdapter, prompt_loader: GenerationPromptLoader | None = None) -> None:
        self._sk = sk_adapter
        self._prompts = prompt_loader or GenerationPromptLoader()

    def is_configured(self) -> bool:
        return self._sk.is_configured()

    def _task_for_section(self, section: SectionDefinition) -> str:
        # Complex tables (e.g. UAT test cases with cross-references) get the
        # stronger model + higher reasoning effort.
        if section.is_complex:
            return "complex_section"
        return "table_generation"

    async def generate(
        self,
        *,
        section: SectionDefinition,
        retrieval_payload: dict[str, object] | None,
        doc_type: str,
        cost_tracker: GenerationCostTracker,
        parent_title: str | None = None,
        child_titles: list[str] | None = None,
    ) -> dict[str, Any]:
        template = self._prompts.load_template_with_shared_policy("table", section.prompt_selector)
        evidence_context = evidence_text_from_retrieval(retrieval_payload)
        mapping = build_prompt_mapping(
            section,
            doc_type,
            evidence_context,
            parent_section_title=parent_title or "",
            child_section_titles=child_titles or [],
        )
        prompt = self._prompts.render_template(template, mapping)

        task = self._task_for_section(section)
        model = TASK_TO_MODEL[task]

        before = cost_tracker.snapshot()
        raw_text = await self._sk.invoke_text(prompt, task=task, cost_tracker=cost_tracker)
        after = cost_tracker.snapshot()

        t_in, t_out, cost_usd = llm_delta_between_snapshots(before, after)
        normalized_table = _normalize_markdown_table(raw_text.strip())

        return {
            "output_type": "table",
            "content": normalized_table,
            "diagram_path": None,
            "diagram_format": None,
            "tokens_in": t_in,
            "tokens_out": t_out,
            "cost_usd": cost_usd,
            "model": model,
            "task": task,
            "error": None,
        }
