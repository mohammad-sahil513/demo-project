"""JSON-file persistence layer.

Why JSON files? The system is a single-tenant demo that has to be portable
across local dev, Azure Container Apps, and Kubernetes mounts without a SQL
dependency. Each domain object becomes one ``<id>.json`` file under
``storage_root``. The directory layout is:

```
storage/
├── documents/   ← DocumentRecord
├── templates/   ← TemplateRecord
├── workflows/   ← WorkflowRecord
├── outputs/     ← OutputRecord
├── diagrams/    ← rendered diagram images
└── logs/        ← per-workflow log files (see core.logging)
```

Public surface — keep this list in sync with ``api/deps.py``:
"""

from repositories.document_repo import DocumentRepository
from repositories.output_repo import OutputRepository
from repositories.template_repo import TemplateRepository
from repositories.workflow_repo import WorkflowRepository

__all__ = [
    "DocumentRepository",
    "TemplateRepository",
    "WorkflowRepository",
    "OutputRepository",
]
