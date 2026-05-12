"""BRD ingestion pipeline: parse, chunk, index (once per document).

The ingest-once policy lives here: a document is indexed exactly once into
Azure AI Search and subsequent workflows reuse the existing index. See
:class:`IngestionCoordinator` for the gate.

Public surface
--------------
- :class:`DocumentParser`        - Azure Document Intelligence wrapper.
- :class:`DocumentChunker`       - token-aware chunker producing :class:`IngestionChunk`.
- :class:`DocumentIndexer`       - upserts chunks into Azure AI Search.
- :class:`IngestionCoordinator`  - the coordinator that enforces ingest-once.
- :class:`IngestionOrchestrator` - phase entry point called by the workflow.
"""

from modules.ingestion.chunker import DocumentChunker, IngestionChunk
from modules.ingestion.indexer import DocumentIndexer
from modules.ingestion.ingestion_coordinator import IngestionCoordinator, IngestionRunResult
from modules.ingestion.orchestrator import IngestionOrchestrator
from modules.ingestion.parser import DocumentParser

__all__ = [
    "DocumentChunker",
    "DocumentIndexer",
    "DocumentParser",
    "IngestionChunk",
    "IngestionCoordinator",
    "IngestionOrchestrator",
    "IngestionRunResult",
]
