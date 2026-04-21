"""Application settings (pydantic-settings)."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.constants import DOCUMENT_INTELLIGENCE_USD_PER_PAGE


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ai-sdlc-backend"
    app_env: str = "development"
    app_debug: bool = True
    storage_root: Path = Field(default=Path("storage"))

    api_prefix: str = "/api"

    # Kroki must not share the API server port; default 8001.
    kroki_url: str = "http://localhost:8001"

    azure_openai_endpoint: str = ""
    azure_search_endpoint: str = ""
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


settings = Settings()


def ensure_storage_dirs() -> None:
    settings.ensure_storage_dirs()
