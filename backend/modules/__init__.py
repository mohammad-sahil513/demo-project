"""Domain modules — phase implementations for the workflow pipeline.

Each subpackage owns one piece of the workflow:

- ``ingestion``     parse, chunk, and index BRD documents
- ``retrieval``     query Azure AI Search for evidence per section
- ``template``      load, classify, and compile templates
- ``generation``    LLM prompt assembly + section generation (text/table/diagram)
- ``assembly``      normalize generated sections into an ordered document
- ``export``        render assembled content to DOCX/XLSX
- ``observability`` cost rollups + structured logging helpers

The orchestration that drives them lives in :mod:`services.workflow_executor`.
See ``docs/PIPELINE.md`` for the end-to-end flow.
"""
