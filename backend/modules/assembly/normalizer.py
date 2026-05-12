"""Normalize generated section content before export.

The LLM emits prose that mostly matches the prompt contract but occasionally:

- repeats the section title as a heading at the top,
- includes drafting notes (``Traceability notes:``, ``Sources:``),
- writes a generic "this section describes..." lead-in for a parent that
  already has children,
- duplicates paragraphs,
- decorates lines with ``**__text__**`` style emphasis wrappers,
- runs on with 20+ bullets in a parent section.

This module strips those quirks deterministically so the export pipeline
gets clean content. Each transformation appends a short, machine-readable
note to ``NormalizationResult.notes`` for observability.

Order of operations
-------------------
1. Strip the leading duplicated heading.
2. Strip internal-only lines (final-mode export only).
3. Trim parent content where the first child heading appears.
4. Strip decorative emphasis wrappers.
5. Drop generic parent lead-ins when the section has children.
6. Compress oversized parent bullet lists.
7. De-duplicate paragraphs.
8. Collapse excessive blank lines.
9. Final pass through :func:`sanitize_deliverable_markdown` for diagram/transport leakage.
"""
from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass, field

from modules.assembly.content_hygiene import sanitize_deliverable_markdown


@dataclass(frozen=True, slots=True)
class NormalizationResult:
    """Cleaned content + list of transformation notes (one per applied rule)."""

    content: str
    notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Heading normalization / matching
# ---------------------------------------------------------------------------
_HEADING_RE = re.compile(r"^(\\)?(#{1,6})\s+(.+?)\s*$")
_NUMBERING_RE = re.compile(
    r"^(?:[A-Za-z]\.|(?:\d+(?:\.\d+)*)[.)]?)\s+",
    flags=re.IGNORECASE,
)

_DECORATIVE_WRAPPER_PATTERNS = (
    re.compile(r"^\s*\*\*_(.+?)_\*\*\s*$"),
    re.compile(r"^\s*__\*(.+?)\*__\s*$"),
    re.compile(r"^\s*\*\*(.+?)\*\*\s*$"),
)


def _normalize_heading_text(value: str) -> str:
    """Lowercase, strip markdown/numbering/punctuation — used for heading equality.

    NFKC normalization handles ligatures and full-width characters; we then
    drop the ``#`` prefix and any numeric/alpha numbering so a heading is
    equal to itself regardless of formatting variant.
    """
    text = unicodedata.normalize("NFKC", value or "").strip().lower()
    text = re.sub(r"\s+", " ", text)

    m = _HEADING_RE.match(text)
    if m:
        text = m.group(3).strip().lower()

    text = _NUMBERING_RE.sub("", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _is_heading_line(line: str) -> bool:
    return _HEADING_RE.match(line.strip()) is not None


def _matches_section_title(line: str, section_title: str) -> bool:
    if not line.strip() or not section_title.strip():
        return False
    return _normalize_heading_text(line) == _normalize_heading_text(section_title)


# ---------------------------------------------------------------------------
# Internal drafting block stripping
# ---------------------------------------------------------------------------
_INTERNAL_LINE_PREFIXES = (
    "traceability notes",
    "key traceability notes",
    "source ",
    "sources:",
    "source:",
)

_INTERNAL_PLACEHOLDER_PATTERNS = (
    re.compile(r"<<\s*SCREENSHOT_", flags=re.IGNORECASE),
    re.compile(r"\[\s*people\.ey\.com\s*\]", flags=re.IGNORECASE),
)


def _looks_internal_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False

    lowered = stripped.lower()
    for prefix in _INTERNAL_LINE_PREFIXES:
        if lowered.startswith(prefix):
            return True

    for pattern in _INTERNAL_PLACEHOLDER_PATTERNS:
        if pattern.search(stripped):
            return True

    return False


def _strip_internal_lines(
    lines: list[str],
    *,
    section_title: str,
    export_mode: str,
    notes: list[str],
) -> list[str]:
    if export_mode != "final":
        return lines

    keep: list[str] = []
    removed_any = False

    section_title_norm = _normalize_heading_text(section_title)
    preserve_assumption_like = any(
        token in section_title_norm
        for token in ("assumption", "risk", "approval", "reviewer", "dependency")
    )

    i = 0
    while i < len(lines):
        line = lines[i]

        if _looks_internal_line(line):
            removed_any = True
            i += 1

            while i < len(lines) and (
                not lines[i].strip()
                or _looks_internal_line(lines[i])
                or lines[i].strip().startswith("(")
            ):
                i += 1
            continue

        lowered = line.strip().lower()

        if not preserve_assumption_like and lowered in {
            "assumptions and scope notes",
            "constraints and known gaps",
            "recommended immediate mitigations",
            "assumptions and constraints",
            "risks and follow-up",
        }:
            removed_any = True
            i += 1
            while i < len(lines) and lines[i].strip():
                i += 1
            continue

        keep.append(line)
        i += 1

    if removed_any:
        notes.append("internal_drafting_lines_removed")
    return keep


# ---------------------------------------------------------------------------
# Parent/subsection duplication trimming
# ---------------------------------------------------------------------------
def _trim_at_first_child_heading(
    lines: list[str],
    *,
    child_titles: Iterable[str],
    notes: list[str],
) -> list[str]:
    normalized_child_titles = {
        _normalize_heading_text(title)
        for title in child_titles
        if title and str(title).strip()
    }
    if not normalized_child_titles:
        return lines

    for idx, line in enumerate(lines):
        if not line.strip():
            continue
        if _is_heading_line(line):
            norm = _normalize_heading_text(line)
            if norm in normalized_child_titles:
                notes.append("trimmed_from_first_child_heading")
                return lines[:idx]

    return lines


# ---------------------------------------------------------------------------
# Leading duplicate title stripping
# ---------------------------------------------------------------------------
def _strip_leading_duplicate_heading(
    lines: list[str],
    *,
    section_title: str,
    notes: list[str],
) -> list[str]:
    if not lines:
        return lines

    idx = 0
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    if idx >= len(lines):
        return lines

    first = lines[idx]
    if _matches_section_title(first, section_title):
        notes.append("leading_duplicate_heading_removed")
        del lines[idx]

        if idx < len(lines) and not lines[idx].strip():
            del lines[idx]

    return lines


# ---------------------------------------------------------------------------
# Additional paragraph-level cleanup
# ---------------------------------------------------------------------------
_META_PARENT_PARAGRAPH_RE = re.compile(
    r"^(this section|this document|the following section|the following)\b.*"
    r"\b(defines|describes|captures|records|outlines|summarizes|documents|provides)\b",
    flags=re.IGNORECASE,
)


def _normalize_paragraph_key(value: str) -> str:
    text = unicodedata.normalize("NFKC", value or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _split_paragraphs(text: str) -> list[str]:
    if not text.strip():
        return []
    return [part.strip() for part in re.split(r"\n\s*\n", text.strip()) if part.strip()]


def _dedupe_paragraphs(text: str, *, notes: list[str]) -> str:
    paragraphs = _split_paragraphs(text)
    seen: set[str] = set()
    kept: list[str] = []
    removed = False

    for para in paragraphs:
        key = _normalize_paragraph_key(para)
        if not key:
            continue
        if key in seen:
            removed = True
            continue
        seen.add(key)
        kept.append(para)

    if removed:
        notes.append("duplicate_paragraphs_removed")

    return "\n\n".join(kept).strip()


def _remove_generic_parent_leadin(
    text: str,
    *,
    has_children: bool,
    notes: list[str],
) -> str:
    if not has_children:
        return text.strip()

    paragraphs = _split_paragraphs(text)
    if not paragraphs:
        return ""

    cleaned: list[str] = []
    removed = False

    for idx, para in enumerate(paragraphs):
        if idx == 0 and _META_PARENT_PARAGRAPH_RE.match(para):
            removed = True
            continue
        cleaned.append(para)

    if removed:
        notes.append("generic_parent_meta_leadin_removed")

    return "\n\n".join(cleaned).strip()


def _strip_decorative_emphasis(text: str, *, notes: list[str]) -> str:
    cleaned_lines: list[str] = []
    changed = False

    for line in text.splitlines():
        stripped = line.strip()
        replaced = False
        for pattern in _DECORATIVE_WRAPPER_PATTERNS:
            match = pattern.match(stripped)
            if match:
                cleaned_lines.append(match.group(1).strip())
                changed = True
                replaced = True
                break
        if not replaced:
            cleaned_lines.append(line)

    if changed:
        notes.append("decorative_markdown_emphasis_removed")

    return "\n".join(cleaned_lines).strip()


def _compress_parent_lists(
    text: str,
    *,
    has_children: bool,
    notes: list[str],
) -> str:
    if not has_children:
        return text.strip()

    lines = text.splitlines()
    bullet_re = re.compile(r"^\s*[-*•]\s+.+$")
    bullet_indices = [idx for idx, line in enumerate(lines) if bullet_re.match(line.strip())]

    if len(bullet_indices) <= 6:
        return text.strip()

    keep_indices = set(bullet_indices[:6])
    trimmed_lines: list[str] = []
    removed = False
    for idx, line in enumerate(lines):
        if idx in bullet_indices and idx not in keep_indices:
            removed = True
            continue
        trimmed_lines.append(line)

    if removed:
        notes.append("parent_bullet_list_trimmed")

    return "\n".join(trimmed_lines).strip()


# ---------------------------------------------------------------------------
# Public normalization entry point
# ---------------------------------------------------------------------------
def normalize_section_content(
    *,
    section_title: str,
    content: str,
    child_titles: Iterable[str] = (),
    export_mode: str = "final",
) -> NormalizationResult:
    """Normalize generated content before export.

    See the module docstring for the full ordered list of transformations.
    Each rule appends a note when it actually changes the content so the
    workflow record can show *which* hygiene rules fired.

    Args:
        section_title: The section's own title — used to detect/remove the
            common "model repeats the heading" pattern.
        content: Raw LLM output.
        child_titles: Titles of immediate-or-nested children. When non-empty
            the section is treated as a parent and parent-specific rules
            (lead-in stripping, bullet compression) activate.
        export_mode: ``"final"`` (default) or ``"preview"``. Preview mode
            keeps internal drafting lines so reviewers can see what the
            generator emitted.
    """
    if not content:
        return NormalizationResult(content="", notes=[])

    notes: list[str] = []
    lines = content.splitlines()

    lines = _strip_leading_duplicate_heading(
        lines,
        section_title=section_title,
        notes=notes,
    )

    lines = _strip_internal_lines(
        lines,
        section_title=section_title,
        export_mode=export_mode,
        notes=notes,
    )

    lines = _trim_at_first_child_heading(
        lines,
        child_titles=child_titles,
        notes=notes,
    )

    text = "\n".join(lines).strip()
    text = _strip_decorative_emphasis(text, notes=notes)
    text = _remove_generic_parent_leadin(
        text,
        has_children=any(str(title).strip() for title in child_titles),
        notes=notes,
    )
    text = _compress_parent_lists(
        text,
        has_children=any(str(title).strip() for title in child_titles),
        notes=notes,
    )
    text = _dedupe_paragraphs(text, notes=notes)

    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    hygiene = sanitize_deliverable_markdown(text)
    if hygiene.notes:
        notes.extend(hygiene.notes)
    text = hygiene.text

    return NormalizationResult(content=text, notes=notes)
