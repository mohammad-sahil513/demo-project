import json
import os
import sys
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv
load_dotenv()

ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "").rstrip("/")
API_KEY = os.getenv("AZURE_SEARCH_API_KEY", "").strip()
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME", "sdlc-chunks").strip()
API_VERSION = os.getenv("AZURE_SEARCH_API_VERSION", "2025-09-01").strip()
EXPECTED_DIMENSIONS = int(os.getenv("AZURE_SEARCH_VECTOR_DIMENSIONS", "1536"))

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


def get_index(index_name: str) -> Dict[str, Any]:
    return request("GET", f"/indexes/{index_name}", [200])


def get_field(index_def: Dict[str, Any], field_name: str) -> Optional[Dict[str, Any]]:
    for field in index_def.get("fields", []):
        if field.get("name") == field_name:
            return field
    return None


def check_equal(errors: List[str], actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        errors.append(f"{label}: expected {expected!r}, got {actual!r}")


def check_true(errors: List[str], actual: Any, label: str) -> None:
    if actual is not True:
        errors.append(f"{label}: expected True, got {actual!r}")


def check_false(errors: List[str], actual: Any, label: str) -> None:
    if actual is not False:
        errors.append(f"{label}: expected False, got {actual!r}")


def validate_schema(index_def: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    # Required fields and core checks
    required_fields = {
        "chunk_id": "Edm.String",
        "document_id": "Edm.String",
        "workflow_run_id": "Edm.String",
        "text": "Edm.String",
        "chunk_index": "Edm.Int32",
        "section_heading": "Edm.String",
        "page_number": "Edm.Int32",
        "content_type": "Edm.String",
        "embedding": "Collection(Edm.Single)",
    }

    for field_name, expected_type in required_fields.items():
        field = get_field(index_def, field_name)
        if not field:
            errors.append(f"Missing field: {field_name}")
            continue
        check_equal(errors, field.get("type"), expected_type, f"{field_name}.type")

    # chunk_id
    field = get_field(index_def, "chunk_id")
    if field:
        check_true(errors, field.get("key"), "chunk_id.key")
        check_true(errors, field.get("filterable"), "chunk_id.filterable")

    # document_id
    field = get_field(index_def, "document_id")
    if field:
        check_true(errors, field.get("filterable"), "document_id.filterable")

    # workflow_run_id
    field = get_field(index_def, "workflow_run_id")
    if field:
        check_true(errors, field.get("filterable"), "workflow_run_id.filterable")

    # text
    field = get_field(index_def, "text")
    if field:
        check_true(errors, field.get("searchable"), "text.searchable")

    # chunk_index
    field = get_field(index_def, "chunk_index")
    if field:
        check_true(errors, field.get("filterable"), "chunk_index.filterable")
        check_true(errors, field.get("sortable"), "chunk_index.sortable")

    # page_number
    field = get_field(index_def, "page_number")
    if field:
        check_true(errors, field.get("filterable"), "page_number.filterable")
        check_true(errors, field.get("sortable"), "page_number.sortable")

    # content_type
    field = get_field(index_def, "content_type")
    if field:
        check_true(errors, field.get("filterable"), "content_type.filterable")

    # embedding
    field = get_field(index_def, "embedding")
    if field:
        check_true(errors, field.get("searchable"), "embedding.searchable")
        check_false(errors, field.get("filterable"), "embedding.filterable")
        check_false(errors, field.get("sortable"), "embedding.sortable")
        check_false(errors, field.get("facetable"), "embedding.facetable")
        check_equal(errors, field.get("dimensions"), EXPECTED_DIMENSIONS, "embedding.dimensions")
        check_equal(errors, field.get("vectorSearchProfile"), "vector-profile", "embedding.vectorSearchProfile")

    # vectorSearch config
    vector_search = index_def.get("vectorSearch", {})
    algorithms = vector_search.get("algorithms", [])
    profiles = vector_search.get("profiles", [])

    algo_names = {a.get("name"): a for a in algorithms if a.get("name")}
    profile_names = {p.get("name"): p for p in profiles if p.get("name")}

    if "hnsw-config" not in algo_names:
        errors.append("vectorSearch.algorithms missing 'hnsw-config'")
    else:
        check_equal(errors, algo_names["hnsw-config"].get("kind"), "hnsw", "vectorSearch.algorithms[hnsw-config].kind")

    if "vector-profile" not in profile_names:
        errors.append("vectorSearch.profiles missing 'vector-profile'")
    else:
        check_equal(
            errors,
            profile_names["vector-profile"].get("algorithm"),
            "hnsw-config",
            "vectorSearch.profiles[vector-profile].algorithm",
        )

    return errors


def main() -> None:
    require_config()

    print("=== Azure AI Search Schema Validator ===")
    print(f"Endpoint            : {ENDPOINT}")
    print(f"Index name          : {INDEX_NAME}")
    print(f"API version         : {API_VERSION}")
    print(f"Expected dimensions : {EXPECTED_DIMENSIONS}")

    index_def = get_index(INDEX_NAME)

    print("\nLive schema summary:")
    print(json.dumps(
        {
            "name": index_def.get("name"),
            "field_names": [f.get("name") for f in index_def.get("fields", [])],
            "vectorSearch": index_def.get("vectorSearch", {}),
        },
        indent=2
    ))

    errors = validate_schema(index_def)

    if errors:
        print("\n❌ VALIDATION FAILED")
        for err in errors:
            print(f" - {err}")
        sys.exit(1)

    print("\n✅ VALIDATION PASSED")
    print("The live index schema matches the expected backend contract.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nFATAL: {exc}")
        sys.exit(1)
