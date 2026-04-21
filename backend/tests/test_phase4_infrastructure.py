from __future__ import annotations

import asyncio

import pytest

from core.config import settings
from infrastructure.doc_intelligence import AzureDocIntelligenceClient
from infrastructure.search_client import AzureSearchClient, SearchChunk
from infrastructure.sk_adapter import AzureSKAdapter


def test_doc_intelligence_table_to_markdown_conversion() -> None:
    adapter = AzureDocIntelligenceClient(endpoint="https://example", api_key="test")
    table = {
        "rowCount": 2,
        "columnCount": 2,
        "cells": [
            {"rowIndex": 0, "columnIndex": 0, "content": "Col A"},
            {"rowIndex": 0, "columnIndex": 1, "content": "Col B"},
            {"rowIndex": 1, "columnIndex": 0, "content": "1"},
            {"rowIndex": 1, "columnIndex": 1, "content": "2"},
        ],
    }

    markdown = adapter._table_to_markdown(table)

    assert "| Col A | Col B |" in markdown
    assert "| --- | --- |" in markdown
    assert "| 1 | 2 |" in markdown


def test_sk_adapter_json_parser_handles_fenced_content() -> None:
    adapter = AzureSKAdapter(endpoint="https://example", api_key="test")
    payload = """```json
{"key":"value","count":2}
```"""

    parsed = adapter._parse_json_payload(payload)

    assert parsed == {"key": "value", "count": 2}


def test_search_client_filter_escaping_and_chunk_shape() -> None:
    client = AzureSearchClient(endpoint="https://search.example", api_key="key", index_name="idx")
    filter_clause = client.build_document_filter("doc-'x'")
    assert filter_clause == "document_id eq 'doc-''x'''"

    chunk = SearchChunk(
        chunk_id="chk-1",
        document_id="doc-1",
        workflow_run_id="wf-1",
        text="hello",
        chunk_index=0,
        section_heading="Overview",
        page_number=1,
        content_type="text",
        embedding=[0.1, 0.2],
    )
    assert chunk.chunk_id == "chk-1"
    assert chunk.embedding == [0.1, 0.2]


@pytest.mark.skipif(
    not (
        settings.azure_openai_endpoint
        and settings.azure_openai_api_key
        and settings.azure_openai_gpt5mini_deployment
    ),
    reason="SKIPPED (No Azure Creds)",
)
def test_sk_adapter_live_embedding_call() -> None:
    adapter = AzureSKAdapter()
    embedding = asyncio.run(adapter.generate_embedding("phase4 connectivity check"))
    assert isinstance(embedding, list)
    assert len(embedding) > 0


@pytest.mark.skipif(
    not (settings.azure_document_intelligence_endpoint and settings.azure_document_intelligence_key),
    reason="SKIPPED (No Azure Creds)",
)
def test_doc_intelligence_live_call() -> None:
    adapter = AzureDocIntelligenceClient()
    # Minimal PDF payload for connectivity checks only.
    sample_pdf = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF"
    result = asyncio.run(adapter.analyze_document(sample_pdf, content_type="application/pdf"))
    assert result.page_count >= 0
