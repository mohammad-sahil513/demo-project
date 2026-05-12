"""LLM text section generation.

For each ``output_type="text"`` section, this generator:

1. Loads the appropriate prompt YAML (selector-aware) and prepends the
   shared deliverable policy fragment.
2. Builds the prompt mapping via
   :func:`modules.generation.context.build_prompt_mapping`.
3. Calls Azure OpenAI through the SK adapter (``text_generation`` task
   or ``complex_section`` for sections marked ``is_complex``).
4. Post-processes the raw text — strips meta lead-ins, decorative
   wrappers, oversized parent bullet lists, and duplicate paragraphs.

Note: there is intentional overlap between the post-processing here and
``modules.assembly.normalizer``. The generator's pass keeps the workflow's
``section_generation_results`` clean; the assembler runs again on the
final document to catch anything that survived (and to apply rules that
depend on section ordering, like trimming at the next child heading).
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any

from core.constants import TASK_TO_MODEL
from infrastructure.sk_adapter import AzureSKAdapter
from modules.generation.context import build_prompt_mapping, evidence_text_from_retrieval
from modules.generation.cost_tracking import GenerationCostTracker, llm_delta_between_snapshots
from modules.generation.prompt_loader import GenerationPromptLoader
from modules.template.models import SectionDefinition


_META_LEADIN_RE = re.compile(
    r"^(this section|this document|the following section|the following)\b.*"
    r"\b(defines|describes|captures|records|outlines|summarizes|documents|provides)\b",
    flags=re.IGNORECASE,
)

_DECORATIVE_WRAPPER_PATTERNS = (
    re.compile(r"^\s*\*\*_(.+?)_\*\*\s*$"),
    re.compile(r"^\s*__\*(.+?)\*__\s*$"),
    re.compile(r"^\s*\*\*(.+?)\*\*\s*$"),
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


def _dedupe_paragraphs(text: str) -> str:
    paragraphs = _split_paragraphs(text)
    seen: set[str] = set()
    kept: list[str] = []

    for para in paragraphs:
        key = _normalize_paragraph_key(para)
        if not key:
            continue
        if key in seen:
            continue
        seen.add(key)
        kept.append(para)

    return "\n\n".join(kept).strip()


def _remove_generic_parent_leadin(text: str, *, has_children: bool) -> str:
    """
    For parent sections, drop the first paragraph if it is a generic
    'This section provides/defines/describes ...' lead-in.
    """
    if not has_children:
        return text.strip()

    paragraphs = _split_paragraphs(text)
    if not paragraphs:
        return ""

    cleaned: list[str] = []
    for idx, para in enumerate(paragraphs):
        if idx == 0 and _META_LEADIN_RE.match(para):
            continue
        cleaned.append(para)

    return "\n\n".join(cleaned).strip()


def _strip_decorative_emphasis(text: str) -> str:
    """
    Remove full-line decorative wrappers like **_..._**, **...**, etc.,
    while preserving the inner text.
    """
    cleaned_lines: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        replaced = False
        for pattern in _DECORATIVE_WRAPPER_PATTERNS:
            match = pattern.match(stripped)
            if match:
                cleaned_lines.append(match.group(1).strip())
                replaced = True
                break
        if not replaced:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def _tighten_parent_bullets(text: str, *, has_children: bool) -> str:
    """
    Parent sections should stay compact. If a parent section contains too many
    bullets, keep the first few to avoid re-writing child-section detail.
    """
    if not has_children:
        return text.strip()

    lines = text.splitlines()
    bullet_indices: list[int] = []
    bullet_re = re.compile(r"^\s*[-*•]\s+.+$")
    for idx, line in enumerate(lines):
        if bullet_re.match(line.strip()):
            bullet_indices.append(idx)

    if len(bullet_indices) <= 6:
        return text.strip()

    keep_indices = set(bullet_indices[:6])
    trimmed_lines: list[str] = []
    for idx, line in enumerate(lines):
        if idx in bullet_indices and idx not in keep_indices:
            continue
        trimmed_lines.append(line)

    return "\n".join(trimmed_lines).strip()


def _postprocess_text_output(
    text: str,
    *,
    child_titles: list[str] | None,
) -> str:
    cleaned = (text or "").strip()
    cleaned = _strip_decorative_emphasis(cleaned)
    cleaned = _remove_generic_parent_leadin(
        cleaned,
        has_children=bool(child_titles),
    )
    cleaned = _tighten_parent_bullets(
        cleaned,
        has_children=bool(child_titles),
    )
    cleaned = _dedupe_paragraphs(cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned


class TextSectionGenerator:
    """Generates prose section content. Stateless; safe to share across sections."""

    def __init__(self, sk_adapter: AzureSKAdapter, prompt_loader: GenerationPromptLoader | None = None) -> None:
        self._sk = sk_adapter
        self._prompts = prompt_loader or GenerationPromptLoader()

    def is_configured(self) -> bool:
        return self._sk.is_configured()

    def _task_for_section(self, section: SectionDefinition) -> str:
        """Complex sections route to ``gpt-5`` (high reasoning); rest use ``gpt-5-mini``."""
        if section.is_complex:
            return "complex_section"
        return "text_generation"

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
        """Generate prose for one section and return the GenerationSectionResult dict.

        The returned dict shape is validated by ``GenerationSectionResult`` in
        the assembler — extending it requires updating both ends in lockstep.
        """
        template = self._prompts.load_template_with_shared_policy("text", section.prompt_selector)
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
        final_text = _postprocess_text_output(
            raw_text.strip(),
            child_titles=child_titles,
        )

        return {
            "output_type": "text",
            "content": final_text,
            "diagram_path": None,
            "diagram_format": None,
            "tokens_in": t_in,
            "tokens_out": t_out,
            "cost_usd": cost_usd,
            "model": model,
            "task": task,
            "error": None,
        }
