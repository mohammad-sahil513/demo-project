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
    azure_openai_gpt5_deployment: str = "gpt5"
    azure_openai_gpt5mini_deployment: str = "gpt5mini"
    azure_openai_embedding_deployment: str = "text-embedding-3-large"
    azure_openai_endpoint: str = ""

    azure_search_api_key: str = ""
    azure_search_index_name: str = "sdlc-chunks"
    azure_search_endpoint: str = ""
    retrieval_top_k: int = 5
    chunker_token_mode: str = "tiktoken"

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


settings = Settings()


def ensure_storage_dirs() -> None:
    settings.ensure_storage_dirs()
