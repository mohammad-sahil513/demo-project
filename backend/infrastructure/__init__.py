"""Infrastructure adapters for external Azure services.

This package isolates *all* Azure SDK calls behind small, easy-to-mock
adapter classes. Application code (``modules``, ``services``) imports the
adapter classes from here — never the underlying SDK directly. That lets us:

- Mock the entire network in tests with one ``MagicMock`` per adapter.
- Swap implementations (e.g. for a non-Azure fallback) without touching
  business logic.
- Centralize retry, timeout, and observability concerns per integration.

Adapters
--------
- :class:`AzureSKAdapter`            Azure OpenAI chat + embedding adapter.
- :class:`AzureSearchClient`         Azure AI Search indexing + hybrid search.
- :class:`AzureDocIntelligenceClient` Azure Document Intelligence layout API.
"""

from infrastructure.doc_intelligence import AzureDocIntelligenceClient
from infrastructure.search_client import AzureSearchClient
from infrastructure.sk_adapter import AzureSKAdapter

__all__ = [
    "AzureDocIntelligenceClient",
    "AzureSKAdapter",
    "AzureSearchClient",
]
