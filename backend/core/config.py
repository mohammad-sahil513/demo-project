"""Application settings (pydantic-settings)."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.constants import DOCUMENT_INTELLIGENCE_USD_PER_PAGE

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ai-sdlc-backend"
    app_env: str = "development"
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
    storage_root: Path = Field(default=Path("storage"))

    api_prefix: str = "/api"

    # Comma-separated browser origins, or "*" for any origin (SSE + API on another host).
    # With "*", credentials are disabled (browser rules). Example: https://app.example.com,https://www.example.com
    cors_origins: str = "*"

    # Kroki must not share the API server port; default 8001.
    kroki_url: str = "http://localhost:8001"

    azure_openai_api_key: str = ""
    azure_openai_api_version: str = "2024-02-01"
    azure_openai_gpt5_deployment: str = "gpt-5"
    azure_openai_gpt5mini_deployment: str = "gpt-5-mini"
    azure_openai_embedding_deployment: str = "text-embedding-3-small"
    azure_openai_endpoint: str = ""

    azure_search_api_key: str = ""
    azure_search_index_name: str = "sdlc-chunks"
    azure_search_endpoint: str = ""
    retrieval_top_k: int = 5
    chunker_token_mode: str = "tiktoken"
    header_detection_mode: str = "strict_row1"
    header_scan_max_rows: int = 5
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
    # Post-export: normalize document.xml so page 1 is title, page 2 is TOC, then body (all DOCX paths).
    template_docx_structure_fixer_enabled: bool = True
    # Compile: LLM section classification timeout and retries (asyncio.wait_for per attempt).
    template_classifier_timeout_seconds: float = 120.0
    template_classifier_max_retries: int = 2

    azure_document_intelligence_key: str = ""
    azure_document_intelligence_endpoint: str = ""

    # Cost model (USD) — Document Intelligence prebuilt-layout, per page (env: DOCUMENT_INTELLIGENCE_USD_PER_PAGE).
    document_intelligence_usd_per_page: float = Field(default=DOCUMENT_INTELLIGENCE_USD_PER_PAGE)

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
        raw = (self.cors_origins or "").strip()
        if not raw or raw == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]

    def cors_allow_credentials(self) -> bool:
        """Wildcard origin is incompatible with credentialed cross-origin requests."""
        return self.cors_origin_list() != ["*"]

    def app_env_normalized(self) -> str:
        return str(self.app_env or "").strip().lower()

    def is_local_env(self) -> bool:
        return self.app_env_normalized() in {"local", "development", "dev"}

    def is_strict_env(self) -> bool:
        return self.app_env_normalized() in {"staging", "production"}


settings = Settings()


def ensure_storage_dirs() -> None:
    settings.ensure_storage_dirs()
