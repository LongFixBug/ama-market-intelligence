from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import re
import secrets
import sys
import uuid
from contextlib import asynccontextmanager
from time import time
from typing import Any

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Path, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from sse_starlette.sse import EventSourceResponse

from ml.agents.content_models import CampaignStatus

from .rate_limit import InMemoryRateLimiter
from .schemas import AnalyzeRequest, ContentCampaignRequest
from .services.analysis_jobs import SQLiteAnalysisJobStore
from .services.content_campaigns import ContentCampaignService

# Ensure root workspace is in sys.path so the backend can import the ml package.
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

env_path = os.path.join(root_dir, "backend/.env")
if os.path.exists(env_path):
    # Runtime environment variables take precedence over .env values.
    load_dotenv(env_path, override=False)
else:
    load_dotenv(override=False)

logger = logging.getLogger("ama.backend")

LOCAL_FRONTEND_ORIGINS = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
)

_TERMINAL_JOB_STAGES = {"completed", "error"}


def _env_int(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        value = default
    return max(minimum, min(value, maximum))


def _cors_origins() -> list[str]:
    raw_origins = os.getenv("CORS_ORIGINS", ",".join(LOCAL_FRONTEND_ORIGINS))
    origins = [origin.strip().rstrip("/") for origin in raw_origins.split(",") if origin.strip()]
    if not origins or "*" in origins:
        logger.warning("Ignoring wildcard CORS_ORIGINS; configure explicit frontend origins")
        return list(LOCAL_FRONTEND_ORIGINS)
    return origins


IS_PRODUCTION = os.getenv("APP_ENV", "development").lower() == "production"
MAX_ACTIVE_JOBS = _env_int("MAX_ACTIVE_JOBS", 4, 1, 100)
MAX_PENDING_JOBS = _env_int("MAX_PENDING_JOBS", 100, 1, 10_000)
JOB_QUEUE_SIZE = _env_int("JOB_QUEUE_SIZE", 32, 4, 256)
JOB_TTL_SECONDS = _env_int("JOB_TTL_SECONDS", 300, 30, 3600)
ANALYSIS_TIMEOUT_SECONDS = _env_int("ANALYSIS_TIMEOUT_SECONDS", 120, 10, 600)
RATE_LIMIT_REQUESTS = _env_int("ANALYZE_RATE_LIMIT", 5, 1, 1000)
RATE_LIMIT_WINDOW_SECONDS = _env_int("ANALYZE_RATE_WINDOW_SECONDS", 60, 1, 3600)
CONTENT_RATE_LIMIT_REQUESTS = _env_int("CONTENT_RATE_LIMIT", 30, 1, 1000)
CONTENT_RATE_LIMIT_WINDOW_SECONDS = _env_int("CONTENT_RATE_WINDOW_SECONDS", 60, 1, 3600)
JOB_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{8,64}$")

# Live queues remain process-local for low-latency SSE, while job auth/event
# history is durable on the current host. Multi-host deployments still need
# Redis/Postgres plus pub/sub/queue coordination.
JOB_QUEUES: dict[str, asyncio.Queue[dict[str, Any]]] = {}
JOB_TOKENS: dict[str, str] = {}
JOB_RUNNING: set[str] = set()
JOB_LOCK = asyncio.Lock()
ACTIVE_JOBS = asyncio.Semaphore(MAX_ACTIVE_JOBS)
RATE_LIMITER = InMemoryRateLimiter(RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW_SECONDS)
CONTENT_RATE_LIMITER = InMemoryRateLimiter(
    CONTENT_RATE_LIMIT_REQUESTS,
    CONTENT_RATE_LIMIT_WINDOW_SECONDS,
)
ANALYSIS_JOBS = SQLiteAnalysisJobStore(
    os.getenv(
        "ANALYSIS_JOB_STORE_PATH",
        os.path.join("backend", ".data", "analysis_jobs.sqlite3"),
    )
)
CONTENT_CAMPAIGNS = ContentCampaignService()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Persisted analysis jobs cannot be resumed safely after an abrupt process
    # restart, so convert them to a terminal error that the original client can
    # replay with its existing stream token.
    await ANALYSIS_JOBS.cleanup_expired(time() - JOB_TTL_SECONDS)
    recovered = await ANALYSIS_JOBS.recover_interrupted(
        "Tiến trình phân tích bị gián đoạn do backend khởi động lại; vui lòng chạy lại."
    )
    if recovered:
        logger.warning("Recovered interrupted analysis jobs", extra={"count": recovered})

    # Restore scheduled campaign work. Publishing already in-flight is handled
    # conservatively by the campaign service.
    await CONTENT_CAMPAIGNS.recover()
    try:
        yield
    finally:
        await CONTENT_CAMPAIGNS.shutdown()


app = FastAPI(
    title="AMA Market Intelligence API Gateway",
    description="Backend API Gateway for Multi-Agent Market Analysis",
    version="1.0.0",
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Last-Event-ID", "Idempotency-Key"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    if request.url.scheme == "https":
        response.headers.setdefault(
            "Strict-Transport-Security",
            "max-age=31536000; includeSubDomains",
        )
    return response


def _client_key(request: Request) -> str:
    # Do not trust arbitrary X-Forwarded-For until a trusted proxy is configured.
    return request.client.host if request.client else "unknown"


def _campaign_bearer(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=403, detail={"code": "campaign_forbidden"})
    scheme, _, value = authorization.partition(" ")
    if scheme.lower() != "bearer" or not value.strip():
        raise HTTPException(status_code=403, detail={"code": "campaign_forbidden"})
    return value.strip()


def _job_token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def _enforce_rate_limit(
    request: Request,
    limiter: InMemoryRateLimiter = RATE_LIMITER,
    message: str = "Too many analysis requests",
) -> None:
    allowed, retry_after = await limiter.check(_client_key(request))
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail={"code": "rate_limit_exceeded", "message": message},
            headers={"Retry-After": str(retry_after)},
        )


async def _publish(
    job_id: str,
    queue: asyncio.Queue[dict[str, Any]],
    payload: dict[str, Any],
) -> dict[str, Any]:
    # Persist before fan-out so reconnect/restart can replay every accepted
    # event, including the terminal result.
    event = await ANALYSIS_JOBS.append_event(job_id, payload)
    try:
        queue.put_nowait(event)
    except asyncio.QueueFull:
        # Progress messages are disposable from the live queue because the
        # durable log is authoritative; preserve the terminal result if possible.
        if event.get("stage") not in _TERMINAL_JOB_STAGES:
            return event
        try:
            queue.get_nowait()
        except asyncio.QueueEmpty:
            pass
        try:
            queue.put_nowait(event)
        except asyncio.QueueFull:
            logger.error("Unable to publish terminal event because the job queue is full")
    return event


async def _expire_job(job_id: str) -> None:
    await asyncio.sleep(JOB_TTL_SECONDS)
    async with JOB_LOCK:
        JOB_QUEUES.pop(job_id, None)
        JOB_TOKENS.pop(job_id, None)
        JOB_RUNNING.discard(job_id)
    await ANALYSIS_JOBS.delete(job_id)


async def _run_job(job_id: str, topic: str, queue: asyncio.Queue[dict[str, Any]]) -> None:
    async def event_callback(stage: str, message: str, report: dict[str, Any] | None = None):
        payload: dict[str, Any] = {"stage": stage, "message": message}
        if report is not None:
            payload["report"] = report
        await _publish(job_id, queue, payload)

    try:
        async with ACTIVE_JOBS:
            from ml.pipelines.market_analysis_pipeline import execute_market_pipeline

            result = await asyncio.wait_for(
                execute_market_pipeline(topic, event_callback),
                timeout=ANALYSIS_TIMEOUT_SECONDS,
            )
            snapshot = await ANALYSIS_JOBS.load(job_id)
            if snapshot is not None and str(snapshot.get("status") or "") not in _TERMINAL_JOB_STAGES:
                await _publish(
                    job_id,
                    queue,
                    {
                        "stage": "completed",
                        "message": "✅ Đã hoàn tất báo cáo chiến lược!",
                        "report": result,
                    },
                )
    except asyncio.TimeoutError:
        logger.warning("Analysis timed out", extra={"job_id": job_id})
        await _publish(
            job_id,
            queue,
            {
                "stage": "error",
                "message": "Phân tích quá thời gian cho phép; vui lòng thử lại.",
                "code": "analysis_timeout",
            },
        )
    except Exception:
        logger.exception("Analysis pipeline failed", extra={"job_id": job_id})
        try:
            await _publish(
                job_id,
                queue,
                {
                    "stage": "error",
                    "message": "Dịch vụ phân tích tạm thời không khả dụng.",
                    "code": "analysis_failed",
                },
            )
        except Exception:
            logger.exception("Unable to persist terminal analysis error", extra={"job_id": job_id})
    finally:
        async with JOB_LOCK:
            JOB_RUNNING.discard(job_id)
        asyncio.create_task(_expire_job(job_id))


async def _start_job(
    job_id: str,
    request: Request,
    req: AnalyzeRequest,
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    await _enforce_rate_limit(
        request,
        limiter=RATE_LIMITER,
        message="Too many analysis requests",
    )

    if not JOB_ID_PATTERN.fullmatch(job_id):
        raise HTTPException(status_code=422, detail={"code": "invalid_job_id"})

    token = secrets.token_urlsafe(32)
    queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=JOB_QUEUE_SIZE)

    async with JOB_LOCK:
        if len(JOB_RUNNING) >= MAX_PENDING_JOBS:
            raise HTTPException(
                status_code=503,
                detail={"code": "job_capacity_reached", "message": "Analysis queue is full"},
                headers={"Retry-After": "30"},
            )
        if (
            job_id in JOB_QUEUES
            or job_id in JOB_RUNNING
            or await ANALYSIS_JOBS.exists(job_id)
        ):
            raise HTTPException(
                status_code=409,
                detail={"code": "job_already_exists", "message": "Job already exists"},
            )

        created = await ANALYSIS_JOBS.create(
            job_id,
            _job_token_digest(token),
            req.topic,
        )
        if not created:
            raise HTTPException(
                status_code=409,
                detail={"code": "job_already_exists", "message": "Job already exists"},
            )

        JOB_QUEUES[job_id] = queue
        JOB_TOKENS[job_id] = token
        JOB_RUNNING.add(job_id)

    background_tasks.add_task(_run_job, job_id, req.topic, queue)
    return {
        "status": "accepted",
        "job_id": job_id,
        "stream_token": token,
        "topic": req.topic,
    }


@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "AMA Backend API Gateway",
        "version": "1.0.0",
    }


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "AMA Backend API Gateway"}


@app.post("/api/analyze", status_code=202)
async def trigger_analysis(req: AnalyzeRequest, request: Request, background_tasks: BackgroundTasks):
    job_id = uuid.uuid4().hex
    return await _start_job(job_id, request, req, background_tasks)


@app.post("/api/analyze/{job_id}", status_code=202)
async def trigger_analysis_legacy(
    req: AnalyzeRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    job_id: str = Path(min_length=8, max_length=64, pattern=r"^[A-Za-z0-9_-]+$"),
):
    return await _start_job(job_id, request, req, background_tasks)


@app.post("/api/content-campaigns", status_code=202)
async def create_content_campaign(
    req: ContentCampaignRequest,
    request: Request,
    background_tasks: BackgroundTasks,
):
    await _enforce_rate_limit(
        request,
        limiter=CONTENT_RATE_LIMITER,
        message="Too many content campaign requests",
    )
    campaign_id, campaign_token = await CONTENT_CAMPAIGNS.create(
        report=req.report,
        platforms=req.platforms,
        canonical_url=str(req.canonical_url) if req.canonical_url else None,
        approval_required=req.approval_required,
        scheduled_at=req.scheduled_at,
    )
    background_tasks.add_task(CONTENT_CAMPAIGNS.run_draft, campaign_id)
    return {
        "status": "accepted",
        "campaign_id": campaign_id,
        "campaign_token": campaign_token,
        "platforms": [platform.value for platform in req.platforms],
    }


@app.get("/api/content-campaigns/{campaign_id}/stream")
async def stream_content_campaign(
    campaign_id: str,
    request: Request,
    stream_token: str | None = Query(default=None, min_length=20, max_length=256),
    last_event_id: int | None = Header(default=None, alias="Last-Event-ID"),
):
    await _enforce_rate_limit(
        request,
        limiter=CONTENT_RATE_LIMITER,
        message="Too many content campaign requests",
    )
    if stream_token is None:
        raise HTTPException(status_code=403, detail={"code": "campaign_forbidden"})
    return EventSourceResponse(
        CONTENT_CAMPAIGNS.stream(
            campaign_id,
            stream_token,
            request,
            last_event_id=last_event_id or 0,
        ),
        headers={"Cache-Control": "no-cache, no-store", "X-Accel-Buffering": "no"},
    )


@app.post("/api/content-campaigns/{campaign_id}/stream-ticket")
async def create_content_stream_ticket(
    campaign_id: str,
    request: Request,
    authorization: str | None = Header(default=None),
):
    await _enforce_rate_limit(
        request,
        limiter=CONTENT_RATE_LIMITER,
        message="Too many content campaign requests",
    )
    token = _campaign_bearer(authorization)
    stream_token = await CONTENT_CAMPAIGNS.create_stream_ticket(campaign_id, token)
    return {
        "stream_token": stream_token,
        "expires_in": CONTENT_CAMPAIGNS.stream_ticket_ttl_seconds,
    }


@app.get("/api/content-campaigns/{campaign_id}")
async def get_content_campaign(
    campaign_id: str,
    request: Request,
    authorization: str | None = Header(default=None),
):
    await _enforce_rate_limit(
        request,
        limiter=CONTENT_RATE_LIMITER,
        message="Too many content campaign requests",
    )
    token = _campaign_bearer(authorization)
    campaign = await CONTENT_CAMPAIGNS.snapshot(campaign_id, token)
    return campaign.model_dump(mode="json")


@app.post("/api/content-campaigns/{campaign_id}/approve")
async def approve_content_campaign(
    campaign_id: str,
    request: Request,
    authorization: str | None = Header(default=None),
):
    await _enforce_rate_limit(
        request,
        limiter=CONTENT_RATE_LIMITER,
        message="Too many content campaign requests",
    )
    token = _campaign_bearer(authorization)
    campaign = await CONTENT_CAMPAIGNS.approve(campaign_id, token)
    return {"status": campaign.status.value, "campaign_id": campaign.id}


@app.post("/api/content-campaigns/{campaign_id}/publish", status_code=202)
async def publish_content_campaign(
    campaign_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str | None = Header(default=None),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    await _enforce_rate_limit(
        request,
        limiter=CONTENT_RATE_LIMITER,
        message="Too many content campaign requests",
    )
    token = _campaign_bearer(authorization)
    campaign = await CONTENT_CAMPAIGNS.snapshot(campaign_id, token)
    if campaign.status not in {CampaignStatus.APPROVED, CampaignStatus.SCHEDULED}:
        raise HTTPException(
            status_code=409,
            detail={"code": "campaign_not_approved", "status": campaign.status.value},
        )
    background_tasks.add_task(
        CONTENT_CAMPAIGNS.publish,
        campaign_id,
        token,
        idempotency_key,
    )
    return {"status": "accepted", "campaign_id": campaign_id}


@app.post("/api/content-campaigns/{campaign_id}/cancel")
async def cancel_content_campaign(
    campaign_id: str,
    request: Request,
    authorization: str | None = Header(default=None),
):
    await _enforce_rate_limit(
        request,
        limiter=CONTENT_RATE_LIMITER,
        message="Too many content campaign requests",
    )
    token = _campaign_bearer(authorization)
    campaign = await CONTENT_CAMPAIGNS.cancel(campaign_id, token)
    return {"status": campaign.status.value, "campaign_id": campaign.id}


def _job_event_to_sse(event: dict[str, Any]) -> dict[str, str]:
    return {
        "id": str(event["event_id"]),
        "event": "message",
        "data": json.dumps(event, ensure_ascii=False),
    }


@app.get("/api/stream/{job_id}")
async def stream_agent_progress(
    job_id: str,
    request: Request,
    token: str | None = Query(default=None, min_length=20, max_length=256),
    last_event_id: int | None = Header(default=None, alias="Last-Event-ID"),
):
    if not JOB_ID_PATTERN.fullmatch(job_id):
        raise HTTPException(status_code=422, detail={"code": "invalid_job_id"})

    snapshot = await ANALYSIS_JOBS.load(job_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail={"code": "job_not_found"})

    if token is None or not secrets.compare_digest(
        _job_token_digest(token),
        str(snapshot.get("token_digest") or ""),
    ):
        raise HTTPException(status_code=403, detail={"code": "stream_forbidden"})

    queue = JOB_QUEUES.get(job_id)
    starting_event_id = max(0, last_event_id or 0)

    async def event_generator():
        last_seen = starting_event_id

        # Initial durable replay.
        current = await ANALYSIS_JOBS.load(job_id)
        if current is None:
            return
        for event in current.get("events") or []:
            event_id = int(event.get("event_id") or 0)
            if event_id <= last_seen:
                continue
            last_seen = event_id
            yield _job_event_to_sse(event)
            if event.get("stage") in _TERMINAL_JOB_STAGES:
                return

        if str(current.get("status") or "") in _TERMINAL_JOB_STAGES:
            return

        while True:
            if await request.is_disconnected():
                return

            live_queue = JOB_QUEUES.get(job_id) or queue
            if live_queue is not None:
                try:
                    event = await asyncio.wait_for(live_queue.get(), timeout=5)
                    event_id = int(event.get("event_id") or 0)
                    if event_id > last_seen:
                        last_seen = event_id
                        yield _job_event_to_sse(event)
                        if event.get("stage") in _TERMINAL_JOB_STAGES:
                            return
                    continue
                except asyncio.TimeoutError:
                    pass

            # Poll the durable log so reconnects and requests that land after a
            # restart can catch up even when no in-memory queue exists.
            current = await ANALYSIS_JOBS.load(job_id)
            if current is None:
                return
            emitted = False
            for event in current.get("events") or []:
                event_id = int(event.get("event_id") or 0)
                if event_id <= last_seen:
                    continue
                emitted = True
                last_seen = event_id
                yield _job_event_to_sse(event)
                if event.get("stage") in _TERMINAL_JOB_STAGES:
                    return

            if str(current.get("status") or "") in _TERMINAL_JOB_STAGES:
                return
            if not emitted:
                yield {"event": "ping", "data": "{}"}

    return EventSourceResponse(
        event_generator(),
        headers={"Cache-Control": "no-cache, no-store", "X-Accel-Buffering": "no"},
    )


@app.post("/api/analyze-direct")
async def analyze_direct(req: AnalyzeRequest, request: Request):
    await _enforce_rate_limit(request)

    try:
        async with ACTIVE_JOBS:
            from ml.pipelines.market_analysis_pipeline import execute_market_pipeline

            async def dummy_callback(
                stage: str,
                message: str,
                report: dict[str, Any] | None = None,
            ):
                return None

            raw_report = await asyncio.wait_for(
                execute_market_pipeline(req.topic, dummy_callback),
                timeout=ANALYSIS_TIMEOUT_SECONDS,
            )
            from ml.schemas.market_report import MarketReport

            return MarketReport.model_validate(raw_report).model_dump(mode="json")
    except asyncio.TimeoutError as exc:
        raise HTTPException(status_code=504, detail={"code": "analysis_timeout"}) from exc
    except ValidationError as exc:
        logger.error("Pipeline returned an invalid report: %s", exc)
        raise HTTPException(status_code=502, detail={"code": "invalid_pipeline_output"}) from exc
    except Exception as exc:
        logger.exception("Direct analysis failed")
        raise HTTPException(status_code=502, detail={"code": "analysis_unavailable"}) from exc
