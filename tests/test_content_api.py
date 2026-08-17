from datetime import datetime, timezone

import pytest
from starlette.testclient import TestClient

from backend.app.main import CONTENT_CAMPAIGNS, app
from backend.app.services.campaign_store import InMemoryCampaignStore
from ml.agents.content_agent import ContentCampaignAgent
from ml.schemas.market_report import (
    AIPromptItem,
    MarketReport,
    NicheAnalysis,
    PricingStrategy,
    RiskItem,
    SourceRef,
)


client = TestClient(app)


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def use_deterministic_content_agent(monkeypatch):
    """Keep API tests independent from provider credentials or network access."""
    monkeypatch.setattr(
        CONTENT_CAMPAIGNS,
        "_agent_factory",
        lambda: ContentCampaignAgent(llm_client_factory=None),
    )
    monkeypatch.setattr(CONTENT_CAMPAIGNS, "_store", InMemoryCampaignStore())
    CONTENT_CAMPAIGNS._runtimes.clear()


def report_payload():
    return MarketReport(
        id="rep-api-content",
        topic="khóa học lập trình AI",
        createdAt=datetime.now(timezone.utc).isoformat(),
        niche_analysis=NicheAnalysis(summary="Sinh viên cần lộ trình học thực hành.", growth_potential="Cao"),
        pricing=PricingStrategy(
            price_range="1.000.000 VNĐ - 5.000.000 VNĐ",
            rationale="So sánh từ các khóa học công khai.",
        ),
        risks=[RiskItem(index=1, title="Nội dung nhanh lỗi thời.")],
        seo_keywords=["khóa học lập trình AI"],
        ai_prompts=[AIPromptItem(prompt="Viết outline khóa học.")],
        sources=[SourceRef(title="Nguồn khóa học", url="https://example.com/course")],
    ).model_dump(mode="json")


def test_content_campaign_requires_approval_before_publish(monkeypatch):
    monkeypatch.setenv("PUBLISH_MODE", "mock")
    created = client.post(
        "/api/content-campaigns",
        json={"report": report_payload(), "platforms": ["blog", "x"]},
    )

    assert created.status_code == 202
    data = created.json()
    campaign_id = data["campaign_id"]
    token = data["campaign_token"]

    snapshot = client.get(f"/api/content-campaigns/{campaign_id}", headers=auth(token))
    assert snapshot.status_code == 200
    assert snapshot.json()["status"] == "waiting_approval"

    assert client.get(f"/api/content-campaigns/{campaign_id}?token={token}").status_code == 403

    stream_ticket = client.post(
        f"/api/content-campaigns/{campaign_id}/stream-ticket",
        headers=auth(token),
    )
    assert stream_ticket.status_code == 200
    assert len(stream_ticket.json()["stream_token"]) >= 20

    forbidden = client.post(
        f"/api/content-campaigns/{campaign_id}/publish",
        headers=auth(token),
    )
    assert forbidden.status_code == 409

    approved = client.post(
        f"/api/content-campaigns/{campaign_id}/approve",
        headers=auth(token),
    )
    assert approved.status_code == 200

    published = client.post(
        f"/api/content-campaigns/{campaign_id}/publish",
        headers={**auth(token), "Idempotency-Key": "publish-api-content-001"},
    )
    assert published.status_code == 202

    final_state = client.get(f"/api/content-campaigns/{campaign_id}", headers=auth(token))
    assert final_state.json()["status"] == "completed"
    assert all(draft["provider_post_id"] for draft in final_state.json()["drafts"])
    replayed_stream = client.get(
        f"/api/content-campaigns/{campaign_id}/stream",
        params={"stream_token": stream_ticket.json()["stream_token"]},
    )
    assert replayed_stream.status_code == 200
    assert "completed" in replayed_stream.text


def test_content_campaign_cannot_disable_human_approval():
    response = client.post(
        "/api/content-campaigns",
        json={"report": report_payload(), "platforms": ["x"], "approval_required": False},
    )

    assert response.status_code == 422


def test_content_campaign_rejects_unbounded_schedule():
    response = client.post(
        "/api/content-campaigns",
        json={
            "report": report_payload(),
            "platforms": ["x"],
            "scheduled_at": "2099-01-01T00:00:00Z",
        },
    )

    assert response.status_code == 422
