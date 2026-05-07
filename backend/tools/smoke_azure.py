from __future__ import annotations

import os
import sys
import requests
from dotenv import load_dotenv
load_dotenv()

SEARCH_API_VERSION = "2025-09-01"
OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")


def fail(msg: str, code: int = 1) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(code)


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def info(msg: str) -> None:
    print(f"[INFO] {msg}")


def smoke_ai_search() -> None:
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT", "").rstrip("/")
    api_key = os.getenv("AZURE_SEARCH_API_KEY", "")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "").strip()

    if not endpoint:
        fail("Missing AZURE_SEARCH_ENDPOINT")
    if not api_key:
        fail("Missing AZURE_SEARCH_API_KEY")

    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
    }

    # 1) Basic connectivity + auth check: list indexes
    list_indexes_url = f"{endpoint}/indexes?api-version={SEARCH_API_VERSION}"
    try:
        r = requests.get(list_indexes_url, headers=headers, timeout=20)
    except requests.RequestException as exc:
        fail(f"Could not connect to Azure AI Search: {exc}")

    if r.status_code == 401:
        fail("Azure AI Search unauthorized: API key is invalid or missing.")
    if r.status_code == 403:
        fail("Azure AI Search forbidden: key does not have required permissions.")
    if r.status_code != 200:
        fail(f"Unexpected status while listing indexes: {r.status_code} | {r.text[:500]}")

    ok("Azure AI Search service is reachable and authentication is working.")

    body = r.json()
    indexes = body.get("value", [])
    ok(f"List indexes call succeeded. Index count: {len(indexes)}")

    if indexes:
        info("Indexes available in the service:")
        for idx, item in enumerate(indexes, start=1):
            name = item.get("name", "<unknown>")
            print(f"   {idx}. {name}")
    else:
        info("No indexes found in the service.")

    # 2) Optional: index-specific smoke test
    if index_name:
        stats_url = f"{endpoint}/indexes('{index_name}')/search.stats?api-version={SEARCH_API_VERSION}"
        r2 = requests.get(stats_url, headers=headers, timeout=20)

        if r2.status_code == 404:
            fail(f"Index '{index_name}' does not exist.")
        if r2.status_code == 401:
            fail("Azure AI Search unauthorized when fetching index stats.")
        if r2.status_code == 403:
            fail("Azure AI Search forbidden when fetching index stats.")
        if r2.status_code != 200:
            fail(f"Failed to fetch stats for index '{index_name}': {r2.status_code} | {r2.text[:500]}")

        stats = r2.json()
        ok(
            "Index statistics retrieved successfully: "
            f"documentCount={stats.get('documentCount')}, "
            f"storageSize={stats.get('storageSize')}, "
            f"vectorIndexSize={stats.get('vectorIndexSize')}"
        )


def smoke_azure_openai() -> None:
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
    deployment = os.getenv("AZURE_OPENAI_GPT5_DEPLOYMENT", "").strip()

    if not endpoint:
        fail("Missing AZURE_OPENAI_ENDPOINT")
    if not api_key:
        fail("Missing AZURE_OPENAI_API_KEY")
    if not deployment:
        fail("Missing AZURE_OPENAI_DEPLOYMENT_NAME")

    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
    }

    url = (
        f"{endpoint}/openai/deployments/{deployment}/chat/completions"
        f"?api-version={OPENAI_API_VERSION}"
    )

    payload = {
        "messages": [
            {"role": "system", "content": "You are a smoke test assistant."},
            {"role": "user", "content": "Reply with exactly: Azure OpenAI smoke test passed."},
        ],
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
    except requests.RequestException as exc:
        fail(f"Could not connect to Azure OpenAI: {exc}")

    if r.status_code == 401:
        fail("Azure OpenAI unauthorized: API key is invalid or missing.")
    if r.status_code == 403:
        fail("Azure OpenAI forbidden: key does not have required permissions.")
    if r.status_code == 404:
        fail("Azure OpenAI deployment or endpoint not found.")
    if r.status_code != 200:
        fail(f"Azure OpenAI smoke test failed: {r.status_code} | {r.text[:1000]}")

    body = r.json()
    choices = body.get("choices") or []
    if not choices:
        fail("Azure OpenAI returned 200 OK but no choices were present in the response.")

    message = choices[0].get("message", {})
    content = message.get("content", "")

    ok("Azure OpenAI endpoint is reachable and chat completion succeeded.")
    info(f"Azure OpenAI response preview: {str(content)[:200]}")


def main() -> None:
    print("=== Azure AI Search Smoke Test ===")
    smoke_ai_search()

    print("\n=== Azure OpenAI Smoke Test ===")
    smoke_azure_openai()

    print("\nSmoke test completed successfully.")


if __name__ == "__main__":
    main()
