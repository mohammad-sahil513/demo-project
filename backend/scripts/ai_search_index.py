import argparse
import json
import os
import sys
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
load_dotenv()

ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "").rstrip("/")
API_KEY = os.getenv("AZURE_SEARCH_API_KEY", "").strip()
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME", "sdlc-chunks").strip()
API_VERSION = os.getenv("AZURE_SEARCH_API_VERSION", "2025-09-01").strip()
VECTOR_DIMENSIONS = int(os.getenv("AZURE_SEARCH_VECTOR_DIMENSIONS", "1536"))

TIMEOUT = 60


def require_config() -> None:
    missing = []
    if not ENDPOINT:
        missing.append("AZURE_SEARCH_ENDPOINT")
    if not API_KEY:
        missing.append("AZURE_SEARCH_API_KEY")
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")


def build_url(path: str) -> str:
    return f"{ENDPOINT}{path}?api-version={API_VERSION}"


def headers() -> Dict[str, str]:
    return {
        "Content-Type": "application/json",
        "api-key": API_KEY,
    }


def request(method: str, path: str, expected_statuses: List[int], **kwargs) -> Any:
    response = requests.request(
        method=method,
        url=build_url(path),
        headers=headers(),
        timeout=TIMEOUT,
        **kwargs,
    )

    if response.status_code not in expected_statuses:
        print("\n=== REQUEST FAILED ===")
        print(f"{method} {build_url(path)}")
        print(f"Status: {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2))
        except Exception:
            print(response.text)
        response.raise_for_status()

    if not response.text:
        return None

    try:
        return response.json()
    except Exception:
        return response.text


def list_indexes() -> List[str]:
    data = request("GET", "/indexes", [200])
    names = [item["name"] for item in data.get("value", [])]
    print("\nExisting indexes:")
    if not names:
        print("  (none)")
    else:
        for name in names:
            print(f"  - {name}")
    return names


def delete_index_if_exists(index_name: str) -> None:
    names = list_indexes()
    if index_name not in names:
        print(f"\nIndex '{index_name}' does not exist. Nothing to delete.")
        return

    print(f"\nDeleting index '{index_name}'...")
    request("DELETE", f"/indexes/{index_name}", [204])
    print(f"Deleted index '{index_name}'.")


def build_index_schema(index_name: str) -> Dict[str, Any]:
    return {
        "name": index_name,
        "description": "Chunk index for SDLC document ingestion and hybrid retrieval.",
        "fields": [
            {
                "name": "chunk_id",
                "type": "Edm.String",
                "key": True,
                "searchable": False,
                "filterable": True,
                "sortable": False,
                "facetable": False,
                "retrievable": True,
            },
            {
                "name": "document_id",
                "type": "Edm.String",
                "searchable": False,
                "filterable": True,
                "sortable": False,
                "facetable": False,
                "retrievable": True,
            },
            {
                "name": "workflow_run_id",
                "type": "Edm.String",
                "searchable": False,
                "filterable": True,
                "sortable": False,
                "facetable": False,
                "retrievable": True,
            },
            {
                "name": "text",
                "type": "Edm.String",
                "searchable": True,
                "filterable": False,
                "sortable": False,
                "facetable": False,
                "retrievable": True,
            },
            {
                "name": "chunk_index",
                "type": "Edm.Int32",
                "searchable": False,
                "filterable": True,
                "sortable": True,
                "facetable": False,
                "retrievable": True,
            },
            {
                "name": "section_heading",
                "type": "Edm.String",
                "searchable": False,
                "filterable": False,
                "sortable": False,
                "facetable": False,
                "retrievable": True,
            },
            {
                "name": "page_number",
                "type": "Edm.Int32",
                "searchable": False,
                "filterable": True,
                "sortable": True,
                "facetable": False,
                "retrievable": True,
            },
            {
                "name": "content_type",
                "type": "Edm.String",
                "searchable": False,
                "filterable": True,
                "sortable": False,
                "facetable": True,
                "retrievable": True,
            },
            {
                "name": "embedding",
                "type": "Collection(Edm.Single)",
                "searchable": True,
                "filterable": False,
                "sortable": False,
                "facetable": False,
                "retrievable": False,
                "stored": False,
                "dimensions": VECTOR_DIMENSIONS,
                "vectorSearchProfile": "vector-profile",
            },
        ],
        "vectorSearch": {
            "algorithms": [
                {
                    "name": "hnsw-config",
                    "kind": "hnsw",
                    "hnswParameters": {
                        "m": 4,
                        "efConstruction": 400,
                        "efSearch": 500,
                        "metric": "cosine",
                    },
                }
            ],
            "profiles": [
                {
                    "name": "vector-profile",
                    "algorithm": "hnsw-config",
                }
            ],
        },
    }


def create_index(index_name: str) -> None:
    schema = build_index_schema(index_name)
    print(f"\nCreating index '{index_name}' with API version {API_VERSION}...")
    result = request("POST", "/indexes", [201], json=schema)
    print(f"Created index: {result.get('name', index_name)}")


def get_index(index_name: str) -> Dict[str, Any]:
    return request("GET", f"/indexes/{index_name}", [200])


def index_exists(index_name: str) -> bool:
    names = list_indexes()
    return index_name in names


def create_index_if_missing(index_name: str) -> None:
    if index_exists(index_name):
        print(f"\nIndex '{index_name}' already exists. Nothing to create.")
        return
    create_index(index_name)


def show_index_summary(index_name: str) -> None:
    print("\nFetching index for confirmation...")
    created = get_index(index_name)
    print(
        json.dumps(
            {
                "name": created.get("name"),
                "field_count": len(created.get("fields", [])),
                "vectorSearch": created.get("vectorSearch", {}),
            },
            indent=2,
        )
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Azure AI Search index lifecycle helper.")
    parser.add_argument(
        "action",
        choices=["list", "create-if-missing", "delete-if-exists", "recreate"],
        help="Index lifecycle action to execute.",
    )
    parser.add_argument(
        "--index-name",
        default=INDEX_NAME,
        help=f"Override index name (default: {INDEX_NAME})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    index_name = args.index_name.strip() or INDEX_NAME
    require_config()

    print("=== Azure AI Search Index Manager ===")
    print(f"Endpoint          : {ENDPOINT}")
    print(f"Index name        : {index_name}")
    print(f"API version       : {API_VERSION}")
    print(f"Vector dimensions : {VECTOR_DIMENSIONS}")
    print(f"Action            : {args.action}")

    if args.action == "list":
        list_indexes()
        print("\nDone.")
        return

    if args.action == "create-if-missing":
        create_index_if_missing(index_name)
        show_index_summary(index_name)
    elif args.action == "delete-if-exists":
        delete_index_if_exists(index_name)
    elif args.action == "recreate":
        delete_index_if_exists(index_name)
        create_index(index_name)
        show_index_summary(index_name)

    print("\nFinal index list:")
    list_indexes()
    print("\nDone.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nFATAL: {exc}")
        sys.exit(1)
