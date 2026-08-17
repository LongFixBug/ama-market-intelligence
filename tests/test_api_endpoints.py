import pytest
from starlette.testclient import TestClient
import backend.app.main as main_module
from backend.app.main import app
from unittest.mock import patch

client = TestClient(app)

def test_read_root():
    """Test the root health check endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["service"] == "AMA Backend API Gateway"


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.parametrize("origin", ["http://localhost:3000", "http://127.0.0.1:3000"])
def test_local_frontend_origins_allow_analyze_preflight(origin):
    response = client.options(
        "/api/analyze",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin

def test_trigger_analysis_endpoint():
    """Test triggering a background analysis job"""
    job_id = "test_job_123"
    payload = {"topic": "Mỹ phẩm thuần chay"}
    async def fake_pipeline(topic, event_callback):
        await event_callback("completed", "ok", {"topic": topic})
        return {"topic": topic}

    with patch("ml.pipelines.market_analysis_pipeline.execute_market_pipeline", new=fake_pipeline):
        response = client.post(f"/api/analyze/{job_id}", json=payload)

    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "accepted"
    assert data["job_id"] == job_id
    assert len(data["stream_token"]) >= 20
    assert data["topic"] == "Mỹ phẩm thuần chay"


def test_server_allocates_job_id_for_new_analysis():
    async def fake_pipeline(topic, event_callback):
        await event_callback("completed", "ok", {"topic": topic})
        return {"topic": topic}

    with patch("ml.pipelines.market_analysis_pipeline.execute_market_pipeline", new=fake_pipeline):
        response = client.post("/api/analyze", json={"topic": "kinh doanh kindle"})

    assert response.status_code == 202
    assert len(response.json()["job_id"]) == 32
    assert len(response.json()["stream_token"]) >= 20


def test_analysis_route_uses_its_own_rate_limiter(monkeypatch):
    calls = []

    async def record_rate_limit(request, limiter=main_module.RATE_LIMITER, message=""):
        calls.append((limiter, message))

    async def fake_pipeline(topic, event_callback):
        await event_callback("completed", "ok", {"topic": topic})
        return {"topic": topic}

    monkeypatch.setattr(main_module, "_enforce_rate_limit", record_rate_limit)
    with patch("ml.pipelines.market_analysis_pipeline.execute_market_pipeline", new=fake_pipeline):
        response = client.post("/api/analyze", json={"topic": "rate limiter wiring"})

    assert response.status_code == 202
    assert calls == [(main_module.RATE_LIMITER, "Too many analysis requests")]


def test_invalid_topic_is_rejected_before_pipeline_starts():
    response = client.post("/api/analyze", json={"topic": " "})

    assert response.status_code == 422


def test_stream_requires_job_token():
    async def fake_pipeline(topic, event_callback):
        await event_callback("completed", "ok", {"topic": topic})
        return {"topic": topic}

    with patch("ml.pipelines.market_analysis_pipeline.execute_market_pipeline", new=fake_pipeline):
        accepted = client.post("/api/analyze", json={"topic": "stream security"})

    data = accepted.json()
    job_id = data["job_id"]
    token = data["stream_token"]

    assert client.get(f"/api/stream/{job_id}").status_code == 403
    stream = client.get(f"/api/stream/{job_id}?token={token}")
    assert stream.status_code == 200
    assert "completed" in stream.text
