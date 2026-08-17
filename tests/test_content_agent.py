from datetime import datetime, timezone

import pytest

from ml.agents.content_agent import ContentCampaignAgent, verify_drafts
from ml.agents.content_models import ActionType, CampaignStatus, Platform
from ml.schemas.market_report import (
    AIPromptItem,
    MarketReport,
    NicheAnalysis,
    PricingStrategy,
    RiskItem,
    SourceRef,
)


def make_report() -> MarketReport:
    return MarketReport(
        id="rep-content-test",
        topic="kinh doanh kindle",
        createdAt=datetime.now(timezone.utc).isoformat(),
        niche_analysis=NicheAnalysis(
            summary="Người đọc cần máy đọc sách chính hãng, pin lâu và được hỗ trợ cài đặt.",
            growth_potential="Cao",
        ),
        pricing=PricingStrategy(
            price_range="2.500.000 VNĐ - 4.500.000 VNĐ",
            rationale="Khoảng giá tham khảo từ các nguồn bán lẻ được kiểm tra.",
        ),
        risks=[RiskItem(index=1, title="Nguồn hàng xách tay có thể thiếu bảo hành.")],
        seo_keywords=["máy đọc sách kindle", "kindle paperwhite chính hãng"],
        ai_prompts=[AIPromptItem(prompt="Viết bài so sánh Kindle và Kobo.")],
        sources=[
            SourceRef(
                title="Bảng giá máy đọc sách",
                url="https://example.com/kindle-prices",
                snippet="Kindle Paperwhite được bán trong khoảng giá tham khảo.",
            )
        ],
    )


@pytest.mark.asyncio
async def test_bounded_agent_creates_distinct_drafts_and_waits_for_approval():
    events = []

    async def emit(stage, message, payload=None):
        events.append(stage)

    campaign = await ContentCampaignAgent(llm_client_factory=None).run(
        report=make_report(),
        platforms=[Platform.BLOG, Platform.X, Platform.LINKEDIN],
        canonical_url="https://example.com/kindle",
        campaign_id="campaign-test-001",
        emit=emit,
    )

    assert campaign.status is CampaignStatus.WAITING_APPROVAL
    assert {draft.platform for draft in campaign.drafts} == {
        Platform.BLOG,
        Platform.X,
        Platform.LINKEDIN,
    }
    assert len({draft.body for draft in campaign.drafts}) == 3
    assert ActionType.EXTRACT_CLAIMS in [action.action for action in campaign.actions]
    assert ActionType.VERIFY_DRAFTS in [action.action for action in campaign.actions]
    assert events[-1] == "waiting_approval"


def test_quality_gate_rejects_duplicate_or_banned_copy():
    report = make_report()
    drafts = ContentCampaignAgent(llm_client_factory=None)._build_drafts(
        report,
        [Platform.X, Platform.LINKEDIN],
        canonical_url=None,
        revision=0,
    )
    drafts[1].body = drafts[0].body + " game-changer"

    issues = verify_drafts(report, drafts)

    assert "banned_language" in issues

    drafts[1].body = drafts[0].body
    assert "duplicate_content" in verify_drafts(report, drafts)


def test_quality_gate_rejects_platform_length_overrides():
    report = make_report()
    drafts = ContentCampaignAgent(llm_client_factory=None)._build_drafts(
        report,
        [Platform.X, Platform.LINKEDIN],
        canonical_url=None,
        revision=0,
    )
    drafts[0].body = "x" * 281
    drafts[1].body = "y" * 3001

    issues = verify_drafts(report, drafts)

    assert "x_length" in issues
    assert "linkedin_length" in issues
