"""BRD ingestion: parse, chunk, index (once per document)."""

from modules.ingestion.ingestion_coordinator import (
    IngestionCoordinator,
    IngestionRunResult,
)

__all__ = ["IngestionCoordinator", "IngestionRunResult"]
