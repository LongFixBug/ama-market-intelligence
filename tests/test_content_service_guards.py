import asyncio
from datetime import datetime, timedelta, timezone

import pytest

from backend.app.services.content_campaigns import ContentCampaignService
from backend.app.services.campaign_store import InMemoryCampaignStore
from backend.app.services.publishers import PublisherRegistry
from ml.agents.content_agent import ContentCampaignAgent
from ml.agents.content_models import Platform, PlatformDraft, PublishResult
from tests.test_content_agent import make_report


class SlowPublisher:
    def __init__(self, platform: Platform, delay: float = 0.05):
        self.platform = platform
        self.delay = delay

    async def publish(self, draft: PlatformDraft) -> PublishResult:
        await asyncio.sleep(self.delay)
        return PublishResult(
            platform=self.platform,
            success=True,
            code="published",
            provider_post_id=f"provider-{self.platform.value}",
            published_url=f"https://example.com/{self.platform.value}",
        )

    async def verify(self, draft: PlatformDraft, result: PublishResult) -> bool:
        await asyncio.sleep(self.delay)
        return True


class CountingAgent:
    def __init__(self, counters: list[int]):
        self.counters = counters

    async def run(self, **kwargs):
        self.counters[0] += 1
        self.counters[1] = max(self.counters[1], self.counters[0])
        try:
            await asyncio.sleep(0.05)
            return await ContentCampaignAgent(llm_client_factory=None).run(**kwargs)
        finally:
            self.counters[0] -= 1


def deterministic_agent():
    return ContentCampaignAgent(llm_client_factory=None)


def slow_registry():
    return PublisherRegistry({platform: SlowPublisher(platform) for platform in Platform})


async def build_approved_campaign(service: ContentCampaignService, campaign_id: str):
    identifier, token = await service.create(
        report=make_report(),
        platforms=[Platform.BLOG, Platform.X, Platform.LINKEDIN, Platform.FACEBOOK],
        canonical_url="https://example.com/kindle",
        approval_required=True,
        scheduled_at=None,
    )
    await service.run_draft(identifier)
    await service.approve(identifier, token)
    return identifier, token


@pytest.mark.asyncio
async def test_publish_variants_are_bounded_concurrently():
    service = ContentCampaignService(
        agent_factory=deterministic_agent,
        publisher_factory=slow_registry,
        publish_concurrency=4,
        store=InMemoryCampaignStore(),
    )
    campaign_id, token = await build_approved_campaign(service, "campaign-concurrency-001")

    started = asyncio.get_running_loop().time()
    campaign = await service.publish(campaign_id, token, "concurrent-001")
    elapsed = asyncio.get_running_loop().time() - started

    assert campaign.status.value == "completed"
    assert elapsed < 0.25


@pytest.mark.asyncio
async def test_duplicate_content_guard_blocks_second_campaign():
    service = ContentCampaignService(
        agent_factory=deterministic_agent,
        publisher_factory=slow_registry,
        publish_concurrency=4,
        store=InMemoryCampaignStore(),
    )
    first_id, first_token = await build_approved_campaign(service, "campaign-duplicate-001")
    first = await service.publish(first_id, first_token, "duplicate-001")
    assert first.status.value == "completed"

    second_id, second_token = await build_approved_campaign(service, "campaign-duplicate-002")
    second = await service.publish(second_id, second_token, "duplicate-002")

    assert second.status.value == "needs_review"
    assert any(result.code == "duplicate_content_guard" for result in second.publish_results)


@pytest.mark.asyncio
async def test_event_is_fanned_out_to_multiple_subscribers():
    service = ContentCampaignService(agent_factory=deterministic_agent, store=InMemoryCampaignStore())
    campaign_id, _ = await service.create(
        report=make_report(),
        platforms=[Platform.X],
        canonical_url=None,
        approval_required=True,
        scheduled_at=None,
    )
    runtime = service._get_runtime(campaign_id)
    first = asyncio.Queue()
    second = asyncio.Queue()
    runtime.subscribers.update({first, second})

    await service._emit(runtime, "testing", "broadcast", None)

    first_event = await first.get()
    second_event = await second.get()
    assert first_event["stage"] == "testing"
    assert second_event["stage"] == "testing"
    assert first_event["event_id"] == second_event["event_id"]


@pytest.mark.asyncio
async def test_scheduled_publish_is_not_duplicated_and_runs_once():
    service = ContentCampaignService(
        agent_factory=deterministic_agent,
        publisher_factory=slow_registry,
        publish_concurrency=4,
        store=InMemoryCampaignStore(),
    )
    identifier, token = await service.create(
        report=make_report(),
        platforms=[Platform.X],
        canonical_url=None,
        approval_required=True,
        scheduled_at=datetime.now(timezone.utc) + timedelta(seconds=0.2),
    )
    await service.run_draft(identifier)
    await service.approve(identifier, token)

    scheduled = await service.publish(identifier, token, "scheduled-001")
    duplicate_request = await service.publish(identifier, token, "scheduled-001")

    assert scheduled.status.value == "scheduled"
    assert duplicate_request.status.value == "scheduled"
    await asyncio.sleep(0.6)
    final = await service.snapshot(identifier, token)
    assert final.status.value == "completed"
    assert len(final.publish_results) == 1


@pytest.mark.asyncio
async def test_agent_drafts_are_concurrency_bounded():
    counters = [0, 0]
    counting_agent = CountingAgent(counters)
    service = ContentCampaignService(
        agent_factory=lambda: counting_agent,
        agent_concurrency=2,
        store=InMemoryCampaignStore(),
    )
    identifiers = []
    for _ in range(4):
        identifier, _ = await service.create(
            report=make_report(),
            platforms=[Platform.X],
            canonical_url=None,
            approval_required=True,
            scheduled_at=None,
        )
        identifiers.append(identifier)

    await asyncio.gather(*(service.run_draft(identifier) for identifier in identifiers))

    assert counters[1] <= 2
