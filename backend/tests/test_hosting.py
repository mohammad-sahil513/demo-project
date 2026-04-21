from __future__ import annotations

from pathlib import Path

from core.constants import WorkflowStatus
from core.hosting import reconcile_interrupted_workflows, verify_storage_writable
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
