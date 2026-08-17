import asyncio
from datetime import datetime, timedelta, timezone

import pytest

from backend.app.services.campaign_store import SQLiteCampaignStore
from backend.app.services.content_campaigns import ContentCampaignService
from backend.app.services.publishers import PublisherRegistry
from ml.agents.content_agent import ContentCampaignAgent
from ml.agents.content_models import CampaignStatus, Platform
from tests.test_content_agent import make_report


def deterministic_agent():
    return ContentCampaignAgent(llm_client_factory=None)


def mock_registry():
    from backend.app.services.publishers import MockPublisher

    return PublisherRegistry({platform: MockPublisher(platform) for platform in Platform})


class LeaseCountingAgent:
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


@pytest.mark.asyncio
async def test_campaign_state_and_events_survive_service_restart(tmp_path):
    path = tmp_path / "campaigns.sqlite3"
    first = ContentCampaignService(
        agent_factory=deterministic_agent,
        publisher_factory=mock_registry,
        store=SQLiteCampaignStore(path),
    )
    campaign_id, token = await first.create(
        report=make_report(),
        platforms=[Platform.BLOG, Platform.X],
        canonical_url="https://example.com/kindle",
        approval_required=True,
        scheduled_at=None,
    )
    await first.run_draft(campaign_id)

    second = ContentCampaignService(
        agent_factory=deterministic_agent,
        publisher_factory=mock_registry,
        store=SQLiteCampaignStore(path),
    )
    snapshot = await second.snapshot(campaign_id, token)

    assert snapshot.status is CampaignStatus.WAITING_APPROVAL
    assert second._get_runtime(campaign_id).token_digest != token
    stages = [event["stage"] for event in second._get_runtime(campaign_id).event_log]
    assert "planning" in stages
    assert "waiting_approval" in stages


@pytest.mark.asyncio
async def test_interrupted_publish_recovers_to_manual_review(tmp_path):
    path = tmp_path / "campaigns.sqlite3"
    first = ContentCampaignService(
        agent_factory=deterministic_agent,
        publisher_factory=mock_registry,
        store=SQLiteCampaignStore(path),
    )
    campaign_id, token = await first.create(
        report=make_report(),
        platforms=[Platform.X],
        canonical_url=None,
        approval_required=True,
        scheduled_at=None,
    )
    await first.run_draft(campaign_id)
    await first.approve(campaign_id, token)
    runtime = first._get_runtime(campaign_id)
    async with runtime.lock:
        runtime.campaign.status = CampaignStatus.PUBLISHING
        await first._persist(runtime)

    second = ContentCampaignService(
        agent_factory=deterministic_agent,
        publisher_factory=mock_registry,
        store=SQLiteCampaignStore(path),
    )
    recovered = await second.snapshot(campaign_id, token)

    assert recovered.status is CampaignStatus.NEEDS_REVIEW
    assert "process_restarted_during_publish" in recovered.issues
    assert any(event["stage"] == "needs_review" for event in second._get_runtime(campaign_id).event_log)


@pytest.mark.asyncio
async def test_scheduled_campaign_is_restored_and_runs_once(tmp_path):
    path = tmp_path / "campaigns.sqlite3"
    first = ContentCampaignService(
        agent_factory=deterministic_agent,
        publisher_factory=mock_registry,
        store=SQLiteCampaignStore(path),
    )
    scheduled_at = datetime.now(timezone.utc) + timedelta(seconds=0.2)
    campaign_id, token = await first.create(
        report=make_report(),
        platforms=[Platform.X],
        canonical_url=None,
        approval_required=True,
        scheduled_at=scheduled_at,
    )
    await first.run_draft(campaign_id)
    await first.approve(campaign_id, token)
    scheduled = await first.publish(campaign_id, token, "restart-schedule-001")
    assert scheduled.status is CampaignStatus.SCHEDULED
    first_runtime = first._get_runtime(campaign_id)
    if first_runtime.scheduled_task:
        first_runtime.scheduled_task.cancel()
    await asyncio.sleep(0)

    second = ContentCampaignService(
        agent_factory=deterministic_agent,
        publisher_factory=mock_registry,
        store=SQLiteCampaignStore(path),
    )
    await second.recover()
    await asyncio.sleep(0.5)
    recovered = await second.snapshot(campaign_id, token)

    assert recovered.status is CampaignStatus.COMPLETED
    assert len(recovered.publish_results) == 1


@pytest.mark.asyncio
async def test_shared_store_lease_prevents_two_workers_from_running_agent_twice(tmp_path):
    path = tmp_path / "campaigns.sqlite3"
    counters = [0, 0]
    first = ContentCampaignService(
        agent_factory=lambda: LeaseCountingAgent(counters),
        store=SQLiteCampaignStore(path),
    )
    second = ContentCampaignService(
        agent_factory=lambda: LeaseCountingAgent(counters),
        store=SQLiteCampaignStore(path),
    )
    campaign_id, token = await first.create(
        report=make_report(),
        platforms=[Platform.X],
        canonical_url=None,
        approval_required=True,
        scheduled_at=None,
    )

    await asyncio.gather(first.run_draft(campaign_id), second.run_draft(campaign_id))

    assert counters[1] == 1
    assert (await second.snapshot(campaign_id, token)).status is CampaignStatus.WAITING_APPROVAL


class ConnectedRequest:
    async def is_disconnected(self):
        return False


@pytest.mark.asyncio
async def test_stream_falls_back_to_persisted_events_on_another_worker(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTENT_EVENT_POLL_SECONDS", "1")
    path = tmp_path / "campaigns.sqlite3"
    first = ContentCampaignService(
        agent_factory=deterministic_agent,
        publisher_factory=mock_registry,
        store=SQLiteCampaignStore(path),
    )
    second = ContentCampaignService(
        agent_factory=deterministic_agent,
        publisher_factory=mock_registry,
        store=SQLiteCampaignStore(path),
    )
    campaign_id, token = await first.create(
        report=make_report(),
        platforms=[Platform.X],
        canonical_url=None,
        approval_required=True,
        scheduled_at=None,
    )
    await first.run_draft(campaign_id)
    await first.approve(campaign_id, token)
    ticket = await second.create_stream_ticket(campaign_id, token)
    second_runtime = second._get_runtime(campaign_id)
    generator = second.stream(
        campaign_id,
        ticket,
        ConnectedRequest(),
        last_event_id=second_runtime.event_sequence,
    )

    publish_task = asyncio.create_task(first.publish(campaign_id, token, "remote-stream-001"))
    events = []
    try:
        for _ in range(5):
            event = await asyncio.wait_for(generator.__anext__(), timeout=3)
            events.append(event["data"])
            if '"stage": "completed"' in event["data"]:
                break
    finally:
        await generator.aclose()
    await publish_task

    assert any('"stage": "completed"' in event for event in events)
