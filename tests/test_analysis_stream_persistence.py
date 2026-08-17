import asyncio
import hashlib

from starlette.testclient import TestClient

import backend.app.main as main_module
from backend.app.main import app
from backend.app.services.analysis_jobs import SQLiteAnalysisJobStore


def test_stream_replays_persisted_terminal_event_after_live_state_is_gone(tmp_path, monkeypatch):
    store = SQLiteAnalysisJobStore(tmp_path / "analysis.sqlite3")
    token = "persisted-stream-token-123456789"

    async def seed():
        await store.create(
            "job-replay-001",
            hashlib.sha256(token.encode("utf-8")).hexdigest(),
            "kinh doanh kindle",
        )
        await store.append_event(
            "job-replay-001",
            {"stage": "planning", "message": "planning"},
        )
        await store.append_event(
            "job-replay-001",
            {
                "stage": "completed",
                "message": "done",
                "report": {"topic": "kinh doanh kindle"},
            },
        )

    asyncio.run(seed())
    monkeypatch.setattr(main_module, "ANALYSIS_JOBS", store)
    main_module.JOB_QUEUES.pop("job-replay-001", None)
    main_module.JOB_TOKENS.pop("job-replay-001", None)
    main_module.JOB_RUNNING.discard("job-replay-001")

    client = TestClient(app)
    response = client.get(
        f"/api/stream/job-replay-001?token={token}",
        headers={"Last-Event-ID": "1"},
    )

    assert response.status_code == 200
    assert "id: 2" in response.text
    assert '"stage": "completed"' in response.text
    assert '"stage": "planning"' not in response.text


def test_stream_rejects_wrong_token_for_persisted_job(tmp_path, monkeypatch):
    store = SQLiteAnalysisJobStore(tmp_path / "analysis.sqlite3")
    token = "persisted-stream-token-123456789"

    async def seed():
        await store.create(
            "job-auth-001",
            hashlib.sha256(token.encode("utf-8")).hexdigest(),
            "test market",
        )

    asyncio.run(seed())
    monkeypatch.setattr(main_module, "ANALYSIS_JOBS", store)

    client = TestClient(app)
    response = client.get(
        "/api/stream/job-auth-001?token=wrong-token-123456789000000",
    )

    assert response.status_code == 403
