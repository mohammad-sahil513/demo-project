"""Application settings backed by ``pydantic-settings`` (loaded from ``.env``).

This module exposes a single ``settings`` instance that is imported across the
backend. Never re-instantiate :class:`Settings` in application code — doing so
would re-read the environment and may yield a different snapshot.

Conventions
-----------
- Every configurable knob is a typed attribute with a default. Production
  overrides come from environment variables (``.env`` locally; the hosting
  platform's secret store in staging/production).
- ``storage_root`` is the only file-system root the backend writes to. All
  per-domain paths (documents, templates, workflows, outputs, diagrams, logs)
  are computed via ``@property`` so we never duplicate the join logic.
- Feature flags follow a strict naming convention:
  ``template_<area>_<behaviour>_enabled`` / ``..._blocking`` /
  ``..._strict``. Defaults are conservative (off) so that staging/production
  must opt in explicitly via env. See ``core.hosting.strict_policy_violations``.

See ``docs/ARCHITECTURE.md`` and
``docs/OPERATIONS.md`` for the full env-var reference.
"""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.constants import DOCUMENT_INTELLIGENCE_USD_PER_PAGE

# Load ``.env`` once at import time. ``pydantic-settings`` will also read the
# file (because of ``model_config`` below) but calling ``load_dotenv`` early
# ensures plain ``os.environ`` lookups elsewhere see the variables too.
load_dotenv()


class Settings(BaseSettings):
    """Strongly-typed configuration for the backend service.

    Reading order: process environment > ``.env`` file > field defaults.
    Unknown env vars are ignored (``extra="ignore"``) so adding a new variable
    upstream never crashes the service unexpectedly.
    """

    # ``env_file_encoding`` is explicit because Windows installers sometimes
    # write ``.env`` as UTF-16; force UTF-8 to keep behavior deterministic.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App identity ------------------------------------------------------
    app_name: str = "ai-sdlc-backend"
    app_env: str = "development"  # ``development`` | ``staging`` | ``production``
    app_debug: bool = True
    log_level: str = "INFO"
    # Console handler level; use WARNING in noisy environments while keeping file logs detailed.
    log_console_level: str = "WARNING"
    # When True, CLI shows only workflow phase/run progression logs.
    log_console_phase_only: bool = True
    # Startup cleanup for observability logs under storage/logs.
    log_cleanup_enabled: bool = True
    log_retention_days: int = 14
    logs_verbose: bool = False
    # ``Path`` field — ``pydantic`` converts strings transparently.
    storage_root: Path = Field(default=Path("storage"))
    # Storage backend selector: ``local`` (filesystem) or ``blob`` (Azure Blob Storage).
    storage_backend: str = "local"
    # Blob storage connection can be provided either by full connection string
    # or account URL + credential chain from the environment/runtime.
    azure_storage_connection_string: str = ""
    azure_storage_account_url: str = ""
    azure_storage_container: str = "ai-sdlc-storage"

    # HTTP prefix for all public endpoints; frontend dev proxy assumes ``/api``.
    api_prefix: str = "/api"

    # Comma-separated browser origins, or "*" for any origin (SSE + API on another host).
    # With "*", credentials are disabled (browser rules). Example: https://app.example.com,https://www.example.com
    cors_origins: str = "*"

    # Kroki must not share the API server port; default 8001.
    kroki_url: str = "http://localhost:8001"

    @field_validator("kroki_url")
    @classmethod
    def _validate_kroki_url(cls, v: object) -> str:
        """Allow empty string (diagram features off); otherwise enforce URL policy."""
        if v is None:
            return ""
        s = str(v).strip()
        if not s:
            return ""
        from core.kroki_url import validate_kroki_base_url

        return validate_kroki_base_url(s)

    # --- Azure OpenAI ------------------------------------------------------
    azure_openai_api_key: str = ""
    azure_openai_api_version: str = "2024-02-01"
    azure_openai_gpt5_deployment: str = "gpt-5"
    azure_openai_gpt5mini_deployment: str = "gpt-5-mini"
    azure_openai_embedding_deployment: str = "text-embedding-3-small"
    azure_openai_endpoint: str = ""

    # --- Azure AI Search ---------------------------------------------------
    azure_search_api_key: str = ""
    azure_search_index_name: str = "sdlc-chunks"
    azure_search_endpoint: str = ""
    retrieval_top_k: int = 5

    # --- Tokenization / chunking ------------------------------------------
    chunker_token_mode: str = "tiktoken"
    header_detection_mode: str = "strict_row1"
    header_scan_max_rows: int = 5

    # --- Template fidelity feature flags ----------------------------------
    # See ``docs/TEMPLATE_OPERATIONS.md`` for what each flag enforces.
    template_fidelity_strict_enabled: bool = False
    template_fidelity_preview_v2_enabled: bool = False
    # When True, DOCX preview is produced via the same fill path as export (sample content), not a raw copy.
    template_preview_sample_fill_enabled: bool = True
    template_schema_validation_blocking: bool = False
    template_fidelity_media_integrity_blocking: bool = False
    # Placeholder-native DOCX: OOXML-only fills at schema locations (no heading-range deletion).
    template_docx_placeholder_native_enabled: bool = False
    # When True, compile fails if any section in plan has no placeholder binding.
    template_section_binding_strict: bool = False
    # Optional: scrub example/description prose and trim tables on compile (DOCX).
    template_upload_normalize_enabled: bool = False
    # When False, pure heading-based DocxFiller export is blocked (set False in staging/prod for fidelity).
    template_docx_legacy_export_allowed: bool = True
    # When True, custom DOCX export must use placeholder-native path (flag + bindings + schema).
    template_docx_require_native_for_custom: bool = False
    # Post-export: normalize document.xml so page 1 is title, page 2 is TOC, then body.
    template_docx_structure_fixer_enabled: bool = True
    # inbuilt_only: apply fixer only to DocxBuilder outputs (inbuilt / no template file). Preserves custom uploads.
    # all: legacy behavior — also rewrite custom filled DOCX (can break client TOC/cover layout).
    template_docx_structure_fixer_scope: str = "inbuilt_only"
    # Compile: LLM section classification timeout and retries (asyncio.wait_for per attempt).
    template_classifier_timeout_seconds: float = 120.0
    template_classifier_max_retries: int = 2

    # --- Azure Document Intelligence --------------------------------------
    azure_document_intelligence_key: str = ""
    azure_document_intelligence_endpoint: str = ""

    # Cost model (USD) — Document Intelligence prebuilt-layout, per page (env: DOCUMENT_INTELLIGENCE_USD_PER_PAGE).
    document_intelligence_usd_per_page: float = Field(default=DOCUMENT_INTELLIGENCE_USD_PER_PAGE)

    # --- Computed storage paths -------------------------------------------
    # ``@property`` so they always reflect the current ``storage_root`` and
    # so tests that override ``storage_root`` get consistent paths.

    @property
    def documents_path(self) -> Path:
        return self.storage_root / "documents"

    @property
    def templates_path(self) -> Path:
        return self.storage_root / "templates"

    @property
    def workflows_path(self) -> Path:
        return self.storage_root / "workflows"

    @property
    def outputs_path(self) -> Path:
        return self.storage_root / "outputs"

    @property
    def diagrams_path(self) -> Path:
        return self.storage_root / "diagrams"

    @property
    def logs_path(self) -> Path:
        return self.storage_root / "logs"

    def ensure_storage_dirs(self) -> None:
        """Create every storage subdirectory if it is missing.

        Called once from the FastAPI lifespan in ``main.py``. Using
        ``parents=True, exist_ok=True`` makes it idempotent and safe to call
        from tests.
        """
        for path in (
            self.documents_path,
            self.templates_path,
            self.workflows_path,
            self.outputs_path,
            self.diagrams_path,
            self.logs_path,
        ):
            path.mkdir(parents=True, exist_ok=True)

    def cors_origin_list(self) -> list[str]:
        """Parse the comma-separated ``cors_origins`` env value into a list."""
        raw = (self.cors_origins or "").strip()
        # Wildcard is special-cased — return the literal ``"*"`` so Starlette
        # treats it as a true any-origin allow, not a list of one literal URL.
        if not raw or raw == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]

    def cors_allow_credentials(self) -> bool:
        """Wildcard origin is incompatible with credentialed cross-origin requests."""
        return self.cors_origin_list() != ["*"]

    def app_env_normalized(self) -> str:
        # Lowercased + stripped so ``"Production "`` and ``"production"`` are equivalent.
        return str(self.app_env or "").strip().lower()

    def is_local_env(self) -> bool:
        return self.app_env_normalized() in {"local", "development", "dev"}

    def is_strict_env(self) -> bool:
        # ``strict`` envs trigger ``core.hosting.strict_policy_violations``
        # which refuses to start the service if fidelity flags are misconfigured.
        return self.app_env_normalized() in {"staging", "production"}

    def storage_backend_normalized(self) -> str:
        """Return normalized storage backend selector from env."""
        return str(self.storage_backend or "").strip().lower()

    def uses_blob_storage(self) -> bool:
        """True when runtime should use Azure Blob Storage as primary backend."""
        return self.storage_backend_normalized() == "blob"


# Module-level singleton. Import this in business code rather than constructing
# ``Settings()`` directly so the configuration snapshot is consistent.
settings = Settings()


def ensure_storage_dirs() -> None:
    """Module-level wrapper used by ``main.py`` to keep imports flat."""
    settings.ensure_storage_dirs()
