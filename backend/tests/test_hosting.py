from __future__ import annotations

from pathlib import Path
import os
import time

import pytest

from core.config import Settings
from core.constants import WorkflowStatus
from core.hosting import reconcile_interrupted_workflows, run_hosting_startup, strict_policy_violations, verify_storage_writable
from core.logging import cleanup_old_observability_logs
from core.ids import utc_now_iso, workflow_id
from repositories.workflow_models import WorkflowRecord
from repositories.workflow_repo import WorkflowRepository


def test_verify_storage_writable_tmp_dir(tmp_path: Path) -> None:
    assert verify_storage_writable(tmp_path) is True
    assert not (tmp_path / ".storage_write_probe").is_file()


def test_reconcile_marks_running_as_failed(tmp_path: Path) -> None:
    repo = WorkflowRepository(tmp_path / "workflows")
    wid = workflow_id()
    now = utc_now_iso()
    repo.save(
        WorkflowRecord(
            workflow_run_id=wid,
            document_id="doc-test",
            template_id="tpl-inbuilt-pdd",
            doc_type="PDD",
            status=WorkflowStatus.RUNNING.value,
            current_phase="INGESTION",
            created_at=now,
            updated_at=now,
        ),
    )
    n = reconcile_interrupted_workflows(repo)
    assert n == 1
    updated = repo.get_or_raise(wid)
    assert updated.status == WorkflowStatus.FAILED.value
    assert any(e.get("code") == "SERVER_RESTART" for e in updated.errors)


def test_reconcile_ignores_completed(tmp_path: Path) -> None:
    repo = WorkflowRepository(tmp_path / "workflows")
    wid = workflow_id()
    now = utc_now_iso()
    repo.save(
        WorkflowRecord(
            workflow_run_id=wid,
            document_id="doc-test",
            template_id="tpl-inbuilt-pdd",
            doc_type="PDD",
            status=WorkflowStatus.COMPLETED.value,
            created_at=now,
            updated_at=now,
        ),
    )
    assert reconcile_interrupted_workflows(repo) == 0
    assert repo.get_or_raise(wid).status == WorkflowStatus.COMPLETED.value


def test_strict_policy_violations_detects_unsafe_prod_flags() -> None:
    s = Settings(
        app_env="production",
        app_debug=True,
        template_docx_placeholder_native_enabled=False,
        template_section_binding_strict=False,
        template_fidelity_strict_enabled=False,
        template_schema_validation_blocking=False,
        template_fidelity_media_integrity_blocking=False,
        template_docx_legacy_export_allowed=True,
        template_docx_require_native_for_custom=False,
    )
    violations = strict_policy_violations(s)
    assert violations
    assert "app_debug must be false" in violations
    assert "template_docx_legacy_export_allowed must be false" in violations


def test_run_hosting_startup_fails_fast_for_strict_env_violations(tmp_path: Path) -> None:
    s = Settings(app_env="production", storage_root=tmp_path)
    with pytest.raises(RuntimeError):
        run_hosting_startup(s)


def test_cleanup_old_observability_logs_prunes_old_files(tmp_path: Path) -> None:
    logs = tmp_path / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    old_cost = logs / "wf-old_cost.jsonl"
    old_run = logs / "wf-old.log"
    keep_misc = logs / "notes.txt"
    fresh_log = logs / "wf-fresh.log"
    old_cost.write_text("x", encoding="utf-8")
    old_run.write_text("x", encoding="utf-8")
    keep_misc.write_text("x", encoding="utf-8")
    fresh_log.write_text("x", encoding="utf-8")

    old_ts = time.time() - (30 * 24 * 60 * 60)
    os.utime(old_cost, (old_ts, old_ts))
    os.utime(old_run, (old_ts, old_ts))

    deleted = cleanup_old_observability_logs(logs_path=logs, retention_days=14)
    assert deleted == 2
    assert not old_cost.exists()
    assert not old_run.exists()
    assert fresh_log.exists()
    assert keep_misc.exists()
