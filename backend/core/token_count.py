"""Token counting helpers with tiktoken fallback behavior."""

from __future__ import annotations

import re
from functools import lru_cache

_FALLBACK_TOKEN_RE = re.compile(r"\S+")


@lru_cache(maxsize=1)
def _get_encoding():
    try:
        import tiktoken  # type: ignore

        return tiktoken.get_encoding("cl100k_base")
    except Exception:
        return None


def count_tokens(text: str) -> int:
    """Count tokens using tiktoken when available; fallback to whitespace tokens."""
    content = text or ""
    encoding = _get_encoding()
    if encoding is not None:
        try:
            return len(encoding.encode(content))
        except Exception:
            pass
    return len(_FALLBACK_TOKEN_RE.findall(content))
