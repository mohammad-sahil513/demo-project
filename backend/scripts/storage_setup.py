"""Bootstrap storage backend from environment settings.

This script supports two setup modes:
- local: ensure filesystem storage directories exist
- blob: validate Azure Blob connectivity and ensure the target container exists
"""

from __future__ import annotations

import sys

from dotenv import load_dotenv

from core.config import settings

load_dotenv()


def setup_local() -> None:
    """Ensure local filesystem storage paths exist."""
    print("Storage backend: local")
    settings.ensure_storage_dirs()
    print(f"Ensured local storage root: {settings.storage_root}")
    print("Ensured local subdirectories:")
    print(f" - {settings.documents_path}")
    print(f" - {settings.templates_path}")
    print(f" - {settings.workflows_path}")
    print(f" - {settings.outputs_path}")
    print(f" - {settings.diagrams_path}")
    print(f" - {settings.logs_path}")


def setup_blob() -> None:
    """Validate blob configuration and ensure target container exists."""
    print("Storage backend: blob")
    container = (settings.azure_storage_container or "").strip()
    conn_string = (settings.azure_storage_connection_string or "").strip()
    account_url = (settings.azure_storage_account_url or "").strip()

    if not container:
        raise RuntimeError("AZURE_STORAGE_CONTAINER is required when STORAGE_BACKEND=blob")
    if not conn_string and not account_url:
        raise RuntimeError(
            "Provide AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_ACCOUNT_URL when STORAGE_BACKEND=blob"
        )

    try:
        from azure.storage.blob import BlobServiceClient
    except ImportError as exc:
        raise RuntimeError("azure-storage-blob is not installed. Install backend requirements first.") from exc

    if conn_string:
        client = BlobServiceClient.from_connection_string(conn_string)
        print("Using AZURE_STORAGE_CONNECTION_STRING")
    else:
        client = BlobServiceClient(account_url=account_url)
        print("Using AZURE_STORAGE_ACCOUNT_URL")

    container_client = client.get_container_client(container)
    exists = container_client.exists()
    if exists:
        print(f"Container '{container}' already exists.")
    else:
        print(f"Container '{container}' not found. Creating...")
        container_client.create_container()
        print(f"Created container '{container}'.")


def main() -> None:
    """Dispatch setup flow based on STORAGE_BACKEND env value."""
    backend = settings.storage_backend_normalized()
    if backend not in {"local", "blob"}:
        raise RuntimeError(f"Unsupported STORAGE_BACKEND='{settings.storage_backend}'. Use 'local' or 'blob'.")

    if backend == "local":
        setup_local()
    else:
        setup_blob()

    print("Storage setup complete.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FATAL: {exc}")
        sys.exit(1)
