"""Load plain-text generation prompts (YAML files read as UTF-8 templates).

Prompts live under ``backend/prompts/generation/<category>/<selector>.yaml``:

- ``category`` = ``text`` | ``table`` | ``diagram``
- ``selector`` = the section's prompt key (e.g. ``scope``, ``risks``,
  ``architecture``). Falls back to ``default.yaml`` per category when the
  exact selector file is missing — so adding a new section never breaks
  the workflow even if no custom prompt has been authored yet.

``render_template`` substitutes ``{placeholders}`` from a mapping; missing
keys render as empty strings (we want prompts to degrade gracefully when
optional inputs aren't available).
"""

from __future__ import annotations

from pathlib import Path

from core.exceptions import GenerationException


class GenerationPromptLoader:
    """Resolves and renders prompt YAMLs. Construct once per process."""

    def __init__(self, prompts_root: Path | None = None) -> None:
        # Walk up two levels from this file to reach ``backend/`` so we can
        # locate ``prompts/generation`` without relying on cwd.
        backend_root = Path(__file__).resolve().parents[2]
        self._root = prompts_root or (backend_root / "prompts" / "generation")

    @staticmethod
    def render_template(template: str, mapping: dict[str, str]) -> str:
        """``str.format_map`` substitution that turns missing keys into empty strings."""

        class _Missing(dict[str, str]):
            def __missing__(self, key: str) -> str:
                return ""

        return template.format_map(_Missing(mapping))

    def load_template(self, category: str, selector: str) -> str:
        """category: text | table | diagram.

        Falls back to ``<category>/default.yaml`` when the specific selector
        file does not exist; raises :class:`GenerationException` only if the
        default is also missing.
        """
        normalized = self._normalize_selector(selector)
        path = self._root / category / f"{normalized}.yaml"
        if not path.is_file():
            path = self._root / category / "default.yaml"
        if not path.is_file():
            raise GenerationException(f"Missing generation prompt for {category}/{selector}", code="PROMPT_MISSING")
        return path.read_text(encoding="utf-8")

    def load_template_with_shared_policy(self, category: str, selector: str) -> str:
        """Prepend the shared deliverable policy fragment (if present) to a category prompt body.

        The shared fragment lets us tweak global policy (style guides,
        prohibited content) in one file rather than every prompt YAML.
        """
        body = self.load_template(category, selector)
        policy_path = self._root / "_shared_deliverable_policy.txt"
        if not policy_path.is_file():
            return body
        fragment = policy_path.read_text(encoding="utf-8").strip()
        if not fragment:
            return body
        return f"{fragment}\n\n---\n\n{body.lstrip()}"

    @staticmethod
    def _normalize_selector(selector: str) -> str:
        # Selectors are case-insensitive and spaces become underscores so we
        # can author prompts with friendly file names.
        cleaned = (selector or "default").strip().lower().replace(" ", "_")
        return cleaned or "default"
