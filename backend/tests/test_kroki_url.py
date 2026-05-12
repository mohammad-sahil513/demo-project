"""Unit tests for ``core.kroki_url`` and ``Settings.kroki_url`` validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from core.config import Settings
from core.kroki_url import validate_kroki_base_url


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("http://localhost:8001", "http://localhost:8001"),
        ("http://localhost:8001/", "http://localhost:8001"),
        ("https://kroki.example.com/path/", "https://kroki.example.com/path"),
    ],
)
def test_validate_kroki_base_url_accepts_http_https(url: str, expected: str) -> None:
    assert validate_kroki_base_url(url) == expected


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "   ",
        "ftp://localhost:8001",
        "http://",
        "http:///png",
        "http://169.254.169.254/",
        "http://metadata.google.internal/latest/meta-data/",
        "http://user:pass@localhost:8001/",
        "http://localhost:8001/?q=1",
        "http://localhost:8001/#frag",
    ],
)
def test_validate_kroki_base_url_rejects_bad_values(bad: str) -> None:
    with pytest.raises(ValueError):
        validate_kroki_base_url(bad)


def test_settings_kroki_url_normalizes_trailing_slash() -> None:
    s = Settings(kroki_url="http://127.0.0.1:8001/")
    assert s.kroki_url == "http://127.0.0.1:8001"


def test_settings_kroki_url_allows_empty_string() -> None:
    s = Settings(kroki_url="")
    assert s.kroki_url == ""


def test_settings_rejects_metadata_host() -> None:
    with pytest.raises(ValidationError):
        Settings(kroki_url="http://169.254.169.254/latest/meta-data/")
