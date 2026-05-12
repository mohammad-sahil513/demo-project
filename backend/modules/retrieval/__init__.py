"""Retrieval: query Azure AI Search for evidence per template section.

The :class:`SectionRetriever` runs one hybrid (keyword + vector) query per
section in parallel-bounded waves, then :class:`EvidencePackager` builds
prompt-ready :class:`EvidenceBundle` objects with citations attached.

Outputs feed directly into :mod:`modules.generation` — each section's
bundle becomes the context for its LLM call.
"""

from modules.retrieval.packager import Citation, EvidenceBundle, EvidencePackager
from modules.retrieval.retriever import RetrievedChunk, SectionRetriever, merge_retrieval_observability

__all__ = [
    "Citation",
    "EvidenceBundle",
    "EvidencePackager",
    "RetrievedChunk",
    "SectionRetriever",
    "merge_retrieval_observability",
]
