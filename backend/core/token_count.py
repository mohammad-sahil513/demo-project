"""Token counting helpers with a tiktoken fallback.

``tiktoken`` is the authoritative tokenizer for OpenAI/Azure OpenAI models;
however, it is an optional dependency in some deployment environments (and
its import is slow). This module:

- Lazily imports ``tiktoken`` once via :func:`_get_encoding` (LRU-cached).
- Falls back to a whitespace-token regex when ``tiktoken`` is unavailable or
  the encode call fails for any reason.

The fallback over-counts tokens for languages without whitespace word
boundaries (CJK), but it is good enough for the budgeting decisions in
``modules.generation`` where we want a rough order-of-magnitude estimate.
"""

from __future__ import annotations

import re
from functools import lru_cache

# ``\S+`` matches any non-whitespace run. The compiled regex is reused for
# every call; constructing it at module load time keeps :func:`count_tokens`
# hot-path-free of regex compilation.
_FALLBACK_TOKEN_RE = re.compile(r"\S+")


@lru_cache(maxsize=1)
def _get_encoding():
    """Return the cached ``cl100k_base`` encoder or ``None`` if unavailable.

    We use ``cl100k_base`` because every Azure OpenAI ``gpt-4`` / ``gpt-5``
    family model uses this encoder family. ``lru_cache`` keeps the loaded
    BPE in memory across calls.
    """
    try:
        import tiktoken  # type: ignore

        return tiktoken.get_encoding("cl100k_base")
    except Exception:
        # Any failure (missing package, environment without write access to
        # the BPE cache, etc.) is treated as "tiktoken not available".
        return None


def count_tokens(text: str) -> int:
    """Count tokens using tiktoken when available; fall back to whitespace tokens.

    Returns ``0`` for ``None`` or empty input. Wrapped in a defensive try/except
    so a corrupt encoder cannot crash an entire workflow.
    """
    content = text or ""
    encoding = _get_encoding()
    if encoding is not None:
        try:
            return len(encoding.encode(content))
        except Exception:
            # Encoder failure — fall through to the whitespace fallback.
            pass
    return len(_FALLBACK_TOKEN_RE.findall(content))
