import hashlib

import pytest

from backend.app.services.analysis_jobs import SQLiteAnalysisJobStore


@pytest.mark.asyncio
async def test_analysis_job_store_persists_ordered_events(tmp_path):
    store = SQLiteAnalysisJobStore(tmp_path / "analysis.sqlite3")
    token = "stream-token-for-analysis-job"
    created = await store.create(
        "job-persist-001",
        hashlib.sha256(token.encode("utf-8")).hexdigest(),
        "kinh doanh kindle",
    )

    assert created is True
    first = await store.append_event(
        "job-persist-001",
        {"stage": "planning", "message": "planning"},
    )
    second = await store.append_event(
        "job-persist-001",
        {
            "stage": "completed",
            "message": "done",
            "report": {"topic": "kinh doanh kindle"},
        },
    )

    snapshot = await store.load("job-persist-001")
    assert snapshot is not None
    assert first["event_id"] == 1
    assert second["event_id"] == 2
    assert snapshot["status"] == "completed"
    assert [event["event_id"] for event in snapshot["events"]] == [1, 2]
    assert snapshot["token_digest"] != token


@pytest.mark.asyncio
async def test_analysis_job_store_marks_interrupted_jobs_as_terminal_error(tmp_path):
    store = SQLiteAnalysisJobStore(tmp_path / "analysis.sqlite3")
    await store.create("job-restart-001", "digest", "test market")
    await store.append_event(
        "job-restart-001",
        {"stage": "scraping", "message": "collecting"},
    )

    recovered = await store.recover_interrupted("backend restarted")

    snapshot = await store.load("job-restart-001")
    assert recovered == 1
    assert snapshot is not None
    assert snapshot["status"] == "error"
    assert snapshot["events"][-1]["stage"] == "error"
    assert snapshot["events"][-1]["code"] == "process_restarted_during_analysis"
    assert snapshot["events"][-1]["event_id"] == 2
