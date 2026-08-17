from __future__ import annotations

import asyncio
import hashlib
import os
import secrets
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import monotonic, time
from typing import Any, Callable

from fastapi import HTTPException

from ml.agents.content_agent import ContentCampaignAgent
from ml.agents.content_models import (
    ActionRecord,
    ActionType,
    CampaignStatus,
    ContentCampaign,
    Platform,
    PlatformDraft,
    PublishResult,
)
from ml.schemas.market_report import MarketReport

from .campaign_store import CampaignStore, SQLiteCampaignStore
from .publishers import PublisherRegistry, build_publishers

Event = dict[str, Any]

_TERMINAL_STATUSES = {
    CampaignStatus.COMPLETED.value,
    CampaignStatus.NEEDS_REVIEW.value,
    CampaignStatus.FAILED.value,
    CampaignStatus.CANCELLED.value,
}


@dataclass
class CampaignRuntime:
    campaign_id: str
    token_digest: str
    report: MarketReport
    platforms: list[Platform]
    canonical_url: str | None
    approval_required: bool
    scheduled_at: datetime | None
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    campaign: ContentCampaign | None = None
    idempotency_keys: set[str] = field(default_factory=set)
    event_log: deque[Event] = field(default_factory=lambda: deque(maxlen=128))
    subscribers: set[asyncio.Queue[Event]] = field(default_factory=set)
    event_sequence: int = 0
    scheduled_task: asyncio.Task[None] | None = None
    stream_tickets: dict[str, float] = field(default_factory=dict)
    last_access_monotonic: float = field(default_factory=monotonic)
    last_access_epoch: float = field(default_factory=time)
    scheduled_idempotency_key: str | None = None
    recovery_checked: bool = True


class ContentCampaignService:
    """Bounded campaign coordinator.

    Campaign snapshots, event history, idempotency keys and duplicate
    reservations are persisted through a small store contract. SQLite WAL is
    the local default; a production multi-instance deployment should provide a
    Postgres/Redis implementation of the same contract plus pub/sub for live
    cross-worker SSE fan-out.
    """

    def __init__(
        self,
        agent_factory: Callable[[], ContentCampaignAgent] | None = None,
        publisher_factory: Callable[[], PublisherRegistry] | None = None,
        agent_concurrency: int | None = None,
        publish_concurrency: int | None = None,
        duplicate_window_seconds: int | None = None,
        campaign_ttl_seconds: int | None = None,
        max_campaigns: int | None = None,
        store: CampaignStore | None = None,
        store_path: str | None = None,
    ):
        self._runtimes: dict[str, CampaignRuntime] = {}
        self._lock = asyncio.Lock()
        self._recovery_lock = asyncio.Lock()
        self._recovered = False
        self._lease_owner_id = uuid.uuid4().hex
        configured_store_path = store_path or os.getenv(
            "CAMPAIGN_STORE_PATH",
            os.path.join("backend", ".data", "content_campaigns.sqlite3"),
        )
        self._store = store or SQLiteCampaignStore(configured_store_path)
        self._agent_factory = agent_factory or self._default_agent_factory
        self._publisher_factory = publisher_factory or build_publishers
        self._agent_concurrency = self._bounded_int(
            agent_concurrency,
            "CONTENT_AGENT_CONCURRENCY",
            default=4,
            minimum=1,
            maximum=16,
        )
        self._agent_semaphore: asyncio.Semaphore | None = None
        self._agent_semaphore_loop = None
        self._publish_concurrency = self._bounded_int(
            publish_concurrency,
            "PUBLISH_CONCURRENCY",
            default=4,
            minimum=1,
            maximum=8,
        )
        self._publish_semaphore: asyncio.Semaphore | None = None
        self._publish_semaphore_loop = None
        self._duplicate_window_seconds = self._bounded_int(
            duplicate_window_seconds,
            "CONTENT_DUPLICATE_WINDOW_SECONDS",
            default=3600,
            minimum=60,
            maximum=86_400,
        )
        self._campaign_ttl_seconds = self._bounded_int(
            campaign_ttl_seconds,
            "CAMPAIGN_TTL_SECONDS",
            default=1800,
            minimum=60,
            maximum=86_400,
        )
        self._max_campaigns = self._bounded_int(
            max_campaigns,
            "MAX_CAMPAIGNS",
            default=5000,
            minimum=10,
            maximum=100_000,
        )
        self._stream_ticket_ttl_seconds = self._bounded_int(
            None,
            "STREAM_TICKET_TTL_SECONDS",
            default=60,
            minimum=15,
            maximum=600,
        )
        self._lease_seconds = self._bounded_int(
            None,
            "CAMPAIGN_LEASE_SECONDS",
            default=90,
            minimum=30,
            maximum=600,
        )
        self._event_poll_seconds = self._bounded_int(
            None,
            "CONTENT_EVENT_POLL_SECONDS",
            default=5,
            minimum=1,
            maximum=30,
        )
        self._duplicate_lock = asyncio.Lock()
        self._recent_content: dict[tuple[str, str], float] = {}

    @staticmethod
    def _bounded_int(
        explicit: int | None,
        env_name: str,
        default: int,
        minimum: int,
        maximum: int,
    ) -> int:
        if explicit is not None:
            value = explicit
        else:
            try:
                value = int(os.getenv(env_name, str(default)))
            except ValueError:
                value = default
        return max(minimum, min(value, maximum))

    @staticmethod
    def _default_agent_factory() -> ContentCampaignAgent:
        llm_factory = None
        if os.getenv("CONTENT_AGENT_LLM", "true").strip().lower() == "true":
            from ml.core.llm import get_async_openai_client

            llm_factory = get_async_openai_client
        return ContentCampaignAgent(llm_client_factory=llm_factory)

    async def create(
        self,
        report: MarketReport,
        platforms: list[Platform],
        canonical_url: str | None,
        approval_required: bool,
        scheduled_at: datetime | None,
    ) -> tuple[str, str]:
        if not approval_required:
            raise HTTPException(status_code=422, detail={"code": "human_approval_required"})
        self._validate_schedule(scheduled_at)
        unique_platforms = list(dict.fromkeys(platforms))
        if not unique_platforms:
            raise HTTPException(status_code=422, detail={"code": "platform_required"})

        campaign_id = f"campaign-{uuid.uuid4().hex}"
        token = secrets.token_urlsafe(32)
        runtime = CampaignRuntime(
            campaign_id=campaign_id,
            token_digest=self._token_digest(token),
            report=report,
            platforms=unique_platforms,
            canonical_url=canonical_url,
            approval_required=True,
            scheduled_at=scheduled_at,
        )
        await self._store.cleanup_expired(time() - self._campaign_ttl_seconds)
        async with self._lock:
            self._cleanup_expired_locked()
            persisted_count = await self._store.count()
            if max(len(self._runtimes), persisted_count) >= self._max_campaigns:
                raise HTTPException(
                    status_code=503,
                    detail={"code": "campaign_capacity_reached"},
                    headers={"Retry-After": "30"},
                )
            self._runtimes[campaign_id] = runtime
        try:
            await self._persist(runtime, campaign_id=campaign_id)
        except Exception as exc:
            async with self._lock:
                self._runtimes.pop(campaign_id, None)
            raise HTTPException(status_code=503, detail={"code": "campaign_store_unavailable"}) from exc
        return campaign_id, token

    @staticmethod
    def _validate_schedule(scheduled_at: datetime | None) -> None:
        if scheduled_at is None:
            return
        normalized = (
            scheduled_at.astimezone(timezone.utc)
            if scheduled_at.tzinfo
            else scheduled_at.replace(tzinfo=timezone.utc)
        )
        now = datetime.now(timezone.utc)
        if normalized <= now:
            raise HTTPException(status_code=422, detail={"code": "schedule_must_be_future"})
        if (normalized - now).total_seconds() > 31 * 86_400:
            raise HTTPException(status_code=422, detail={"code": "schedule_too_far"})

    async def run_draft(self, campaign_id: str) -> None:
        runtime = await self._ensure_runtime(campaign_id)

        async with runtime.lock:
            if runtime.campaign is not None:
                return
        lease_acquired = await self._store.acquire_lease(
            campaign_id,
            self._lease_owner_id,
            time() + self._lease_seconds,
        )
        if not lease_acquired:
            return

        async def emit(stage: str, message: str, payload: dict[str, Any] | None = None):
            await self._emit(runtime, stage, message, payload)

        try:
            try:
                async with self._get_agent_semaphore():
                    campaign = await self._agent_factory().run(
                        report=runtime.report,
                        platforms=runtime.platforms,
                        canonical_url=runtime.canonical_url,
                        campaign_id=campaign_id,
                        emit=emit,
                        approval_required=True,
                        scheduled_at=runtime.scheduled_at,
                    )
                async with runtime.lock:
                    runtime.campaign = campaign
                    self._touch(runtime)
                    await self._persist(runtime, campaign_id=campaign_id)
            except Exception:
                async with runtime.lock:
                    runtime.campaign = ContentCampaign(
                        id=campaign_id,
                        report_id=runtime.report.id,
                        topic=runtime.report.topic,
                        platforms=runtime.platforms,
                        status=CampaignStatus.FAILED,
                        created_at=datetime.now(timezone.utc),
                        issues=["agent_failed"],
                    )
                    await self._persist(runtime, campaign_id=campaign_id)
                await self._emit(runtime, "failed", "Không thể tạo chiến dịch nội dung.", None)
        finally:
            await self._store.release_lease(campaign_id, self._lease_owner_id)

    async def snapshot(self, campaign_id: str, token: str) -> ContentCampaign:
        runtime = await self._authorize(campaign_id, token)
        if runtime.campaign is None:
            raise HTTPException(status_code=409, detail={"code": "campaign_not_ready"})
        return runtime.campaign

    async def create_stream_ticket(self, campaign_id: str, token: str) -> str:
        runtime = await self._authorize(campaign_id, token)
        ticket = secrets.token_urlsafe(24)
        digest = hashlib.sha256(ticket.encode("utf-8")).hexdigest()
        async with runtime.lock:
            now = time()
            runtime.stream_tickets = {
                key: expiry for key, expiry in runtime.stream_tickets.items() if expiry > now
            }
            runtime.stream_tickets[digest] = now + self._stream_ticket_ttl_seconds
            self._touch(runtime)
            await self._persist(runtime, campaign_id=campaign_id)
        return ticket

    @property
    def stream_ticket_ttl_seconds(self) -> int:
        return self._stream_ticket_ttl_seconds

    async def stream(
        self,
        campaign_id: str,
        stream_token: str,
        request,
        last_event_id: int = 0,
    ) -> Any:
        runtime = await self._authorize_stream(campaign_id, stream_token)
        subscriber: asyncio.Queue[Event] = asyncio.Queue(maxsize=64)
        async with runtime.lock:
            history = [event for event in runtime.event_log if int(event["event_id"]) > last_event_id]
            runtime.subscribers.add(subscriber)
            campaign = runtime.campaign
            self._touch(runtime)

        try:
            last_seen_event_id = last_event_id
            for event in history:
                last_seen_event_id = max(last_seen_event_id, int(event["event_id"]))
                current_status = runtime.campaign.status.value if runtime.campaign is not None else None
                # A reconnect after a failed publish can replay an old
                # terminal event. Only the terminal event matching the
                # current status is allowed to close the stream.
                if event.get("stage") in _TERMINAL_STATUSES and event.get("stage") != current_status:
                    continue
                yield self._sse_event(event)
                if event.get("stage") in _TERMINAL_STATUSES:
                    return

            if campaign is not None and campaign.status.value in _TERMINAL_STATUSES and not history:
                snapshot_event = self._event(
                    runtime,
                    self._status_stage(campaign.status),
                    "Trạng thái chiến dịch hiện tại.",
                    {"campaign": campaign.model_dump(mode="json")},
                )
                yield self._sse_event(snapshot_event)
                return

            while True:
                if await request.is_disconnected():
                    return
                try:
                    event = await asyncio.wait_for(subscriber.get(), timeout=self._event_poll_seconds)
                except asyncio.TimeoutError:
                    # A connection may be held by a different worker than the
                    # one running the agent. The durable event log is a
                    # bounded polling fallback; Redis/Postgres pub/sub is the
                    # lower-latency production option.
                    persisted = await self._store.load(campaign_id)
                    if persisted is not None:
                        persisted_events = persisted.get("event_log") or []
                        persisted_campaign = persisted.get("campaign") or {}
                        persisted_status = persisted_campaign.get("status")
                        emitted_persisted = False
                        for persisted_event in persisted_events:
                            event_id = int(persisted_event.get("event_id", 0))
                            if event_id <= last_seen_event_id:
                                continue
                            last_seen_event_id = event_id
                            if (
                                persisted_event.get("stage") in _TERMINAL_STATUSES
                                and persisted_event.get("stage") != persisted_status
                            ):
                                continue
                            emitted_persisted = True
                            yield self._sse_event(persisted_event)
                            if persisted_event.get("stage") in _TERMINAL_STATUSES:
                                return
                        if persisted_status in _TERMINAL_STATUSES and not emitted_persisted:
                            snapshot_event = {
                                "event_id": max(
                                    last_seen_event_id + 1,
                                    int(persisted.get("event_sequence") or 0),
                                ),
                                "stage": persisted_status,
                                "message": "Trạng thái chiến dịch hiện tại.",
                                "campaign": persisted_campaign,
                            }
                            yield self._sse_event(snapshot_event)
                            return
                    yield {"event": "ping", "data": "{}"}
                    continue
                last_seen_event_id = max(last_seen_event_id, int(event["event_id"]))
                yield self._sse_event(event)
                if event.get("stage") in _TERMINAL_STATUSES:
                    return
        finally:
            async with runtime.lock:
                runtime.subscribers.discard(subscriber)
                self._touch(runtime)

    async def approve(self, campaign_id: str, token: str) -> ContentCampaign:
        runtime = await self._authorize(campaign_id, token)
        if runtime.campaign is None:
            raise HTTPException(status_code=409, detail={"code": "campaign_not_ready"})
        async with runtime.lock:
            if runtime.campaign.status not in {CampaignStatus.WAITING_APPROVAL, CampaignStatus.NEEDS_REVIEW}:
                raise HTTPException(
                    status_code=409,
                    detail={"code": "campaign_not_waiting_approval", "status": runtime.campaign.status.value},
                )
            runtime.campaign.approved_at = datetime.now(timezone.utc)
            runtime.campaign.status = CampaignStatus.APPROVED
            await self._emit(runtime, "approved", "Người dùng đã duyệt chiến dịch.", None)
            return runtime.campaign

    async def publish(self, campaign_id: str, token: str, idempotency_key: str | None) -> ContentCampaign:
        runtime = await self._authorize(campaign_id, token)
        if runtime.campaign is None:
            raise HTTPException(status_code=409, detail={"code": "campaign_not_ready"})
        key = (idempotency_key or f"publish:{campaign_id}").strip()
        if not key or len(key) > 200:
            raise HTTPException(status_code=422, detail={"code": "invalid_idempotency_key"})
        return await self._publish_runtime(campaign_id, runtime, key)

    async def _publish_internal(self, campaign_id: str, idempotency_key: str) -> ContentCampaign:
        """Publish from a restored scheduler without requiring plaintext auth."""
        runtime = await self._ensure_runtime(campaign_id)
        if runtime.campaign is None:
            raise HTTPException(status_code=409, detail={"code": "campaign_not_ready"})
        return await self._publish_runtime(campaign_id, runtime, idempotency_key)

    async def _publish_runtime(
        self,
        campaign_id: str,
        runtime: CampaignRuntime,
        key: str,
    ) -> ContentCampaign:

        async with runtime.lock:
            campaign = runtime.campaign
            if campaign.status is CampaignStatus.COMPLETED:
                return campaign
            if campaign.status is CampaignStatus.SCHEDULED:
                return campaign
            if campaign.status is not CampaignStatus.APPROVED:
                raise HTTPException(
                    status_code=409,
                    detail={"code": "campaign_not_approved", "status": campaign.status.value},
                )
            if campaign.scheduled_at and campaign.scheduled_at > datetime.now(timezone.utc):
                if runtime.scheduled_task is None or runtime.scheduled_task.done():
                    campaign.status = CampaignStatus.SCHEDULED
                    runtime.scheduled_idempotency_key = key
                    await self._emit(runtime, "scheduled", "Chiến dịch đã được xếp lịch đăng.", None)
                    runtime.scheduled_task = asyncio.create_task(
                        self._wait_and_publish(campaign_id, key, campaign.scheduled_at)
                    )
                return campaign
            if key in runtime.idempotency_keys:
                return campaign

            lease_acquired = await self._store.acquire_lease(
                campaign_id,
                self._lease_owner_id,
                time() + self._lease_seconds,
            )
            if not lease_acquired:
                # Another worker owns the campaign. It will persist the next
                # state; callers can poll the snapshot without starting a
                # second provider write.
                return campaign
            try:
                try:
                    return await self._publish_locked_body(runtime, campaign, key)
                except asyncio.CancelledError:
                    raise
                except Exception:
                    campaign.status = CampaignStatus.NEEDS_REVIEW
                    campaign.issues = list(
                        dict.fromkeys([*campaign.issues, "publish_internal_error"])
                    )
                    await self._emit(
                        runtime,
                        "needs_review",
                        "Connector gặp lỗi nội bộ; cần kiểm tra trước khi thử lại.",
                        None,
                    )
                    return campaign
            finally:
                await self._store.release_lease(campaign_id, self._lease_owner_id)

    async def _publish_locked_body(
        self,
        runtime: CampaignRuntime,
        campaign: ContentCampaign,
        idempotency_key: str,
    ) -> ContentCampaign:
        runtime.idempotency_keys.add(idempotency_key)
        campaign.status = CampaignStatus.PUBLISHING
        campaign.step += 1
        campaign.actions.append(
            ActionRecord(
                action=ActionType.PUBLISH_VARIANTS,
                step=campaign.step,
                message="Publish approved platform variants",
                created_at=datetime.now(timezone.utc),
            )
        )
        await self._emit(runtime, "publishing", "Đang đăng song song các biến thể qua connector.", None)

        registry = self._publisher_factory()
        pending_drafts = [draft for draft in campaign.drafts if draft.status != "published"]
        results = await asyncio.gather(
            *(self._publish_one(registry, draft) for draft in pending_drafts),
            return_exceptions=True,
        )
        for draft, result in zip(pending_drafts, results):
            if isinstance(result, Exception):
                result = PublishResult(
                    platform=draft.platform,
                    success=False,
                    code="publish_internal_error",
                    detail="Connector failed before a verified result was returned.",
                )
            campaign.step += 1
            campaign.actions.append(
                ActionRecord(
                    action=ActionType.VERIFY_PUBLICATION,
                    step=campaign.step,
                    message=f"Verify {draft.platform.value} provider result",
                    created_at=datetime.now(timezone.utc),
                )
            )
            campaign.publish_results = [
                previous for previous in campaign.publish_results if previous.platform is not draft.platform
            ]
            campaign.publish_results.append(result)
            if result.success and result.verified:
                draft.status = "published"
                draft.provider_post_id = result.provider_post_id
                draft.published_url = result.published_url
                draft.error_code = None
            else:
                draft.status = "needs_review"
                draft.error_code = result.code
            await self._emit(
                runtime,
                "published" if draft.status == "published" else "publish_failed",
                f"{draft.platform.value}: {result.code}",
                {"platform": draft.platform.value, "result": result.model_dump(mode="json")},
            )

        if all(draft.status == "published" for draft in campaign.drafts):
            campaign.status = CampaignStatus.COMPLETED
            campaign.completed_at = datetime.now(timezone.utc)
            campaign.step += 1
            campaign.actions.append(
                ActionRecord(
                    action=ActionType.COMPLETE,
                    step=campaign.step,
                    message="Complete verified content campaign",
                    created_at=datetime.now(timezone.utc),
                )
            )
            await self._emit(runtime, "completed", "Đã đăng và xác minh toàn bộ nền tảng.", None)
        else:
            campaign.status = CampaignStatus.NEEDS_REVIEW
            campaign.issues = list(dict.fromkeys([*campaign.issues, "publish_incomplete"]))
            await self._emit(runtime, "needs_review", "Một hoặc nhiều nền tảng chưa được xác minh.", None)
        return campaign

    async def _publish_one(self, registry: PublisherRegistry, draft: PlatformDraft) -> PublishResult:
        semaphore = self._get_publish_semaphore()
        async with semaphore:
            reservation = await self._reserve_content(draft)
            if reservation is None:
                return PublishResult(
                    platform=draft.platform,
                    success=False,
                    code="duplicate_content_guard",
                    detail="The same platform content hash was recently published.",
                )
            result = await registry.publish(draft)
            if result.success:
                result.verified = await registry.verify(draft, result)
            # If the provider acknowledged the write but verification failed,
            # retain the reservation: retrying blindly could create a second
            # public post after an unknown timeout/permission error.
            if not result.success:
                await self._release_content(reservation)
            return result

    def _get_publish_semaphore(self) -> asyncio.Semaphore:
        loop = asyncio.get_running_loop()
        if self._publish_semaphore is None or self._publish_semaphore_loop is not loop:
            self._publish_semaphore = asyncio.Semaphore(self._publish_concurrency)
            self._publish_semaphore_loop = loop
        return self._publish_semaphore

    def _get_agent_semaphore(self) -> asyncio.Semaphore:
        loop = asyncio.get_running_loop()
        if self._agent_semaphore is None or self._agent_semaphore_loop is not loop:
            self._agent_semaphore = asyncio.Semaphore(self._agent_concurrency)
            self._agent_semaphore_loop = loop
        return self._agent_semaphore

    async def _reserve_content(self, draft: PlatformDraft) -> tuple[str, str, float] | None:
        normalized = " ".join(draft.body.split()).lower()
        content_hash = draft.content_hash or hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        key = (draft.platform.value, content_hash)
        now = time()
        async with self._duplicate_lock:
            self._recent_content = {
                item: expiry for item, expiry in self._recent_content.items() if expiry > now
            }
            if key in self._recent_content:
                return None
            expiry = now + self._duplicate_window_seconds
            if not await self._store.reserve_content(key[0], key[1], expiry):
                return None
            self._recent_content[key] = expiry
            return (key[0], key[1], expiry)

    async def _release_content(self, reservation: tuple[str, str, float]) -> None:
        key = (reservation[0], reservation[1])
        async with self._duplicate_lock:
            if self._recent_content.get(key) == reservation[2]:
                self._recent_content.pop(key, None)
            await self._store.release_content(reservation[0], reservation[1], reservation[2])

    async def _wait_and_publish(
        self,
        campaign_id: str,
        idempotency_key: str,
        scheduled_at: datetime,
    ) -> None:
        try:
            delay = max(0.0, (scheduled_at - datetime.now(timezone.utc)).total_seconds())
            await asyncio.sleep(delay)
            runtime = await self._ensure_runtime(campaign_id)
            async with runtime.lock:
                if runtime.campaign is None or runtime.campaign.status is not CampaignStatus.SCHEDULED:
                    return
                runtime.scheduled_task = None
                runtime.campaign.status = CampaignStatus.APPROVED
                await self._emit(runtime, "approved", "Đến giờ, chiến dịch bắt đầu publish.", None)
            await self._publish_internal(campaign_id, idempotency_key)
        except asyncio.CancelledError:
            return

    async def cancel(self, campaign_id: str, token: str) -> ContentCampaign:
        runtime = await self._authorize(campaign_id, token)
        if runtime.campaign is None:
            raise HTTPException(status_code=409, detail={"code": "campaign_not_ready"})
        async with runtime.lock:
            if runtime.campaign.status in {CampaignStatus.COMPLETED, CampaignStatus.CANCELLED}:
                return runtime.campaign
            if runtime.scheduled_task and not runtime.scheduled_task.done():
                runtime.scheduled_task.cancel()
                runtime.scheduled_task = None
            runtime.campaign.status = CampaignStatus.CANCELLED
            await self._emit(runtime, "cancelled", "Chiến dịch đã bị hủy.", None)
            return runtime.campaign

    def _get_runtime(self, campaign_id: str) -> CampaignRuntime:
        runtime = self._runtimes.get(campaign_id)
        if runtime is None:
            raise HTTPException(status_code=404, detail={"code": "campaign_not_found"})
        self._touch(runtime)
        return runtime

    async def _ensure_runtime(self, campaign_id: str) -> CampaignRuntime:
        runtime = self._runtimes.get(campaign_id)
        if runtime is None:
            snapshot = await self._store.load(campaign_id)
            if snapshot is None:
                raise HTTPException(status_code=404, detail={"code": "campaign_not_found"})
            runtime = self._hydrate_runtime(snapshot)
            async with self._lock:
                existing = self._runtimes.get(campaign_id)
                if existing is None:
                    self._runtimes[campaign_id] = runtime
                else:
                    runtime = existing
        elif not runtime.lock.locked():
            snapshot = await self._store.load(campaign_id)
            if snapshot is not None:
                await self._refresh_runtime(runtime, snapshot)
        self._touch(runtime)
        await self._prepare_restored_runtime(runtime)
        return runtime

    async def _refresh_runtime(self, runtime: CampaignRuntime, snapshot: dict[str, Any]) -> None:
        """Pull a newer snapshot when a request lands on another worker."""
        loaded_event_sequence = int(snapshot.get("event_sequence") or 0)
        current_status = runtime.campaign.status.value if runtime.campaign else None
        loaded_campaign = snapshot.get("campaign") or {}
        loaded_status = loaded_campaign.get("status")
        if loaded_event_sequence < runtime.event_sequence or (
            loaded_event_sequence == runtime.event_sequence and loaded_status == current_status
        ):
            return
        refreshed = self._hydrate_runtime(snapshot)
        if runtime.lock.locked():
            return
        async with runtime.lock:
            if runtime.event_sequence > loaded_event_sequence:
                return
            runtime.report = refreshed.report
            runtime.platforms = refreshed.platforms
            runtime.canonical_url = refreshed.canonical_url
            runtime.approval_required = refreshed.approval_required
            runtime.scheduled_at = refreshed.scheduled_at
            runtime.campaign = refreshed.campaign
            runtime.idempotency_keys = refreshed.idempotency_keys
            runtime.event_log = refreshed.event_log
            runtime.event_sequence = refreshed.event_sequence
            runtime.stream_tickets = refreshed.stream_tickets
            runtime.last_access_epoch = max(runtime.last_access_epoch, refreshed.last_access_epoch)
            runtime.scheduled_idempotency_key = refreshed.scheduled_idempotency_key
            runtime.recovery_checked = False

    async def _authorize(self, campaign_id: str, token: str) -> CampaignRuntime:
        runtime = await self._ensure_runtime(campaign_id)
        token_digest = self._token_digest(token or "")
        if not token or not secrets.compare_digest(token_digest, runtime.token_digest):
            raise HTTPException(status_code=403, detail={"code": "campaign_forbidden"})
        return runtime

    async def _authorize_stream(self, campaign_id: str, stream_token: str) -> CampaignRuntime:
        runtime = await self._ensure_runtime(campaign_id)
        digest = hashlib.sha256((stream_token or "").encode("utf-8")).hexdigest()
        expiry = runtime.stream_tickets.get(digest)
        if expiry is None or expiry <= time():
            raise HTTPException(status_code=403, detail={"code": "stream_forbidden"})
        return runtime

    async def recover(self) -> None:
        """Restore scheduled work and fail closed for interrupted publishing."""
        async with self._recovery_lock:
            snapshots = await self._store.list_recoverable()
            for snapshot in snapshots:
                campaign_id = str(snapshot.get("campaign_id") or "")
                if campaign_id:
                    await self._ensure_runtime(campaign_id)
            self._recovered = True

    async def shutdown(self) -> None:
        """Release this process' leases during a graceful server shutdown."""
        await self._store.release_owner(self._lease_owner_id)

    async def _prepare_restored_runtime(self, runtime: CampaignRuntime) -> None:
        if runtime.recovery_checked and not (
            runtime.campaign is not None and runtime.campaign.status is CampaignStatus.PUBLISHING
        ):
            return
        async with runtime.lock:
            if runtime.recovery_checked and not (
                runtime.campaign is not None and runtime.campaign.status is CampaignStatus.PUBLISHING
            ):
                return
            runtime.recovery_checked = True
            now = time()
            runtime.stream_tickets = {
                key: expiry for key, expiry in runtime.stream_tickets.items() if expiry > now
            }
            campaign = runtime.campaign
            if campaign is None:
                await self._persist(runtime)
                return
            if campaign.status is CampaignStatus.PUBLISHING:
                if await self._store.lease_active(runtime.campaign_id):
                    # Another worker is still inside the provider call. Do
                    # not misclassify a healthy in-flight write as a crash.
                    await self._persist(runtime)
                    return
                campaign.status = CampaignStatus.NEEDS_REVIEW
                campaign.issues = list(
                    dict.fromkeys([*campaign.issues, "process_restarted_during_publish"])
                )
                await self._emit(
                    runtime,
                    "needs_review",
                    "Tiến trình đăng bị gián đoạn; cần kiểm tra thủ công trước khi thử lại.",
                    None,
                )
                return
            if campaign.status is CampaignStatus.SCHEDULED:
                if campaign.scheduled_at is None:
                    campaign.status = CampaignStatus.NEEDS_REVIEW
                    campaign.issues = list(dict.fromkeys([*campaign.issues, "schedule_missing_time"]))
                    await self._emit(
                        runtime,
                        "needs_review",
                        "Lịch đăng không có thời điểm hợp lệ; cần kiểm tra thủ công.",
                        None,
                    )
                    return
                key = runtime.scheduled_idempotency_key or f"publish:{runtime.campaign_id}"
                if runtime.scheduled_task is None or runtime.scheduled_task.done():
                    runtime.scheduled_task = asyncio.create_task(
                        self._wait_and_publish(runtime.campaign_id, key, campaign.scheduled_at)
                    )
            await self._persist(runtime)

    @staticmethod
    def _token_digest(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def _parse_datetime(value: Any) -> datetime | None:
        if not value:
            return None
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed.astimezone(timezone.utc) if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)

    def _hydrate_runtime(self, snapshot: dict[str, Any]) -> CampaignRuntime:
        campaign_id = str(snapshot.get("campaign_id") or "")
        if not campaign_id:
            raise HTTPException(status_code=503, detail={"code": "campaign_store_invalid"})
        try:
            campaign_payload = snapshot.get("campaign")
            event_log = snapshot.get("event_log") or []
            return CampaignRuntime(
                campaign_id=campaign_id,
                token_digest=str(snapshot["token_digest"]),
                report=MarketReport.model_validate(snapshot["report"]),
                platforms=[Platform(value) for value in snapshot["platforms"]],
                canonical_url=snapshot.get("canonical_url"),
                approval_required=bool(snapshot.get("approval_required", True)),
                scheduled_at=self._parse_datetime(snapshot.get("scheduled_at")),
                campaign=ContentCampaign.model_validate(campaign_payload) if campaign_payload else None,
                idempotency_keys=set(snapshot.get("idempotency_keys") or []),
                event_log=deque(event_log, maxlen=128),
                event_sequence=int(snapshot.get("event_sequence") or 0),
                stream_tickets={
                    str(key): float(expiry)
                    for key, expiry in (snapshot.get("stream_tickets") or {}).items()
                    if float(expiry) > time()
                },
                last_access_epoch=float(snapshot.get("last_access_epoch") or time()),
                scheduled_idempotency_key=snapshot.get("scheduled_idempotency_key"),
                recovery_checked=False,
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise HTTPException(status_code=503, detail={"code": "campaign_store_invalid"}) from exc

    async def _persist(self, runtime: CampaignRuntime, campaign_id: str | None = None) -> None:
        identifier = campaign_id or runtime.campaign_id
        campaign = runtime.campaign
        snapshot = {
            "campaign_id": identifier,
            # Only the digest is persisted; the bearer token is returned once
            # at creation and never written to the database.
            "token_digest": runtime.token_digest,
            "report": runtime.report.model_dump(mode="json"),
            "platforms": [platform.value for platform in runtime.platforms],
            "canonical_url": runtime.canonical_url,
            "approval_required": runtime.approval_required,
            "scheduled_at": runtime.scheduled_at.isoformat() if runtime.scheduled_at else None,
            "campaign": campaign.model_dump(mode="json") if campaign else None,
            "idempotency_keys": sorted(runtime.idempotency_keys),
            "event_log": list(runtime.event_log),
            "event_sequence": runtime.event_sequence,
            "stream_tickets": runtime.stream_tickets,
            "last_access_epoch": runtime.last_access_epoch,
            "scheduled_idempotency_key": runtime.scheduled_idempotency_key,
        }
        await self._store.save(identifier, snapshot)

    async def _emit(
        self,
        runtime: CampaignRuntime,
        stage: str,
        message: str,
        payload: dict[str, Any] | None,
    ) -> None:
        event = self._event(runtime, stage, message, payload)
        runtime.event_log.append(event)
        for subscriber in tuple(runtime.subscribers):
            try:
                subscriber.put_nowait(event)
            except asyncio.QueueFull:
                if stage not in _TERMINAL_STATUSES:
                    continue
                try:
                    subscriber.get_nowait()
                except asyncio.QueueEmpty:
                    pass
                try:
                    subscriber.put_nowait(event)
                except asyncio.QueueFull:
                    continue
        await self._persist(runtime)

    @staticmethod
    def _event(
        runtime: CampaignRuntime,
        stage: str,
        message: str,
        payload: dict[str, Any] | None,
    ) -> Event:
        runtime.event_sequence += 1
        event: Event = {
            "event_id": runtime.event_sequence,
            "stage": stage,
            "message": message,
        }
        if payload:
            event.update(payload)
        if runtime.campaign is not None and "campaign" not in event:
            event["campaign"] = runtime.campaign.model_dump(mode="json")
        return event

    @staticmethod
    def _sse_event(event: Event) -> dict[str, str]:
        import json

        return {
            "id": str(event["event_id"]),
            "event": "message",
            "data": json.dumps(event, ensure_ascii=False),
        }

    def _touch(self, runtime: CampaignRuntime) -> None:
        runtime.last_access_monotonic = monotonic()
        runtime.last_access_epoch = time()

    def _cleanup_expired_locked(self) -> None:
        now = monotonic()
        expired = []
        for campaign_id, runtime in self._runtimes.items():
            status = runtime.campaign.status.value if runtime.campaign else None
            if status in _TERMINAL_STATUSES and now - runtime.last_access_monotonic > self._campaign_ttl_seconds:
                expired.append(campaign_id)
        for campaign_id in expired:
            self._runtimes.pop(campaign_id, None)

    @staticmethod
    def _status_stage(status: CampaignStatus) -> str:
        return status.value
