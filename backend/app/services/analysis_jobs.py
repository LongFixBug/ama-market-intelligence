from __future__ import annotations

import asyncio
import json
import sqlite3
from pathlib import Path
from time import time
from typing import Any

_TERMINAL_STAGES = {"completed", "error"}


class SQLiteAnalysisJobStore:
    """Durable single-process analysis job snapshots and SSE event history.

    This store is intentionally scoped to the current MVP/single-host runtime.
    A distributed deployment should replace it with a shared Postgres/Redis
    implementation plus pub/sub or a durable queue.
    """

    def __init__(self, path: str | Path, max_events: int = 128) -> None:
        self.path = str(path)
        self.max_events = max(16, min(max_events, 512))
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout=10000")
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=NORMAL")
        return connection

    def _initialize(self) -> None:
        connection = self._connect()
        try:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS analysis_jobs (
                    job_id TEXT PRIMARY KEY,
                    token_digest TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    status TEXT NOT NULL,
                    event_sequence INTEGER NOT NULL,
                    created_at_epoch REAL NOT NULL,
                    updated_at_epoch REAL NOT NULL,
                    payload TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_analysis_jobs_status_updated
                    ON analysis_jobs(status, updated_at_epoch);
                """
            )
            connection.commit()
        finally:
            connection.close()

    async def create(self, job_id: str, token_digest: str, topic: str) -> bool:
        return await asyncio.to_thread(self._create_sync, job_id, token_digest, topic)

    def _create_sync(self, job_id: str, token_digest: str, topic: str) -> bool:
        now = time()
        snapshot = {
            "job_id": job_id,
            "token_digest": token_digest,
            "topic": topic,
            "status": "running",
            "event_sequence": 0,
            "events": [],
            "created_at_epoch": now,
            "updated_at_epoch": now,
        }
        connection = self._connect()
        try:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO analysis_jobs
                    (job_id, token_digest, topic, status, event_sequence,
                     created_at_epoch, updated_at_epoch, payload)
                VALUES (?, ?, ?, 'running', 0, ?, ?, ?)
                """,
                (
                    job_id,
                    token_digest,
                    topic,
                    now,
                    now,
                    json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")),
                ),
            )
            connection.commit()
            return cursor.rowcount == 1
        finally:
            connection.close()

    async def load(self, job_id: str) -> dict[str, Any] | None:
        return await asyncio.to_thread(self._load_sync, job_id)

    def _load_sync(self, job_id: str) -> dict[str, Any] | None:
        connection = self._connect()
        try:
            row = connection.execute(
                "SELECT payload FROM analysis_jobs WHERE job_id = ?",
                (job_id,),
            ).fetchone()
            return json.loads(row["payload"]) if row else None
        finally:
            connection.close()

    async def exists(self, job_id: str) -> bool:
        return await asyncio.to_thread(self._exists_sync, job_id)

    def _exists_sync(self, job_id: str) -> bool:
        connection = self._connect()
        try:
            row = connection.execute(
                "SELECT 1 FROM analysis_jobs WHERE job_id = ?",
                (job_id,),
            ).fetchone()
            return row is not None
        finally:
            connection.close()

    async def append_event(self, job_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return await asyncio.to_thread(self._append_event_sync, job_id, payload)

    def _append_event_sync(self, job_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT payload FROM analysis_jobs WHERE job_id = ?",
                (job_id,),
            ).fetchone()
            if row is None:
                raise KeyError(job_id)

            snapshot = json.loads(row["payload"])
            sequence = int(snapshot.get("event_sequence") or 0) + 1
            event = {"event_id": sequence, **payload}
            events = list(snapshot.get("events") or [])
            events.append(event)
            events = events[-self.max_events :]
            stage = str(payload.get("stage") or "")
            status = stage if stage in _TERMINAL_STAGES else "running"
            now = time()
            snapshot.update(
                {
                    "status": status,
                    "event_sequence": sequence,
                    "events": events,
                    "updated_at_epoch": now,
                }
            )
            connection.execute(
                """
                UPDATE analysis_jobs
                SET status = ?, event_sequence = ?, updated_at_epoch = ?, payload = ?
                WHERE job_id = ?
                """,
                (
                    status,
                    sequence,
                    now,
                    json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")),
                    job_id,
                ),
            )
            connection.commit()
            return event
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    async def recover_interrupted(self, message: str) -> int:
        return await asyncio.to_thread(self._recover_interrupted_sync, message)

    def _recover_interrupted_sync(self, message: str) -> int:
        connection = self._connect()
        recovered = 0
        try:
            connection.execute("BEGIN IMMEDIATE")
            rows = connection.execute(
                "SELECT job_id, payload FROM analysis_jobs WHERE status = 'running'"
            ).fetchall()
            now = time()
            for row in rows:
                snapshot = json.loads(row["payload"])
                sequence = int(snapshot.get("event_sequence") or 0) + 1
                event = {
                    "event_id": sequence,
                    "stage": "error",
                    "message": message,
                    "code": "process_restarted_during_analysis",
                }
                events = list(snapshot.get("events") or [])
                events.append(event)
                snapshot.update(
                    {
                        "status": "error",
                        "event_sequence": sequence,
                        "events": events[-self.max_events :],
                        "updated_at_epoch": now,
                    }
                )
                connection.execute(
                    """
                    UPDATE analysis_jobs
                    SET status = 'error', event_sequence = ?, updated_at_epoch = ?, payload = ?
                    WHERE job_id = ?
                    """,
                    (
                        sequence,
                        now,
                        json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")),
                        row["job_id"],
                    ),
                )
                recovered += 1
            connection.commit()
            return recovered
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    async def cleanup_expired(self, cutoff_epoch: float) -> int:
        return await asyncio.to_thread(self._cleanup_expired_sync, cutoff_epoch)

    def _cleanup_expired_sync(self, cutoff_epoch: float) -> int:
        connection = self._connect()
        try:
            cursor = connection.execute(
                """
                DELETE FROM analysis_jobs
                WHERE status IN ('completed', 'error')
                  AND updated_at_epoch < ?
                """,
                (cutoff_epoch,),
            )
            connection.commit()
            return cursor.rowcount
        finally:
            connection.close()

    async def delete(self, job_id: str) -> None:
        await asyncio.to_thread(self._delete_sync, job_id)

    def _delete_sync(self, job_id: str) -> None:
        connection = self._connect()
        try:
            connection.execute("DELETE FROM analysis_jobs WHERE job_id = ?", (job_id,))
            connection.commit()
        finally:
            connection.close()


class InMemoryAnalysisJobStore:
    """Test double with the same contract as the SQLite store."""

    def __init__(self, max_events: int = 128) -> None:
        self.max_events = max_events
        self._jobs: dict[str, dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    @staticmethod
    def _copy(value: dict[str, Any]) -> dict[str, Any]:
        return json.loads(json.dumps(value, ensure_ascii=False))

    async def create(self, job_id: str, token_digest: str, topic: str) -> bool:
        async with self._lock:
            if job_id in self._jobs:
                return False
            now = time()
            self._jobs[job_id] = {
                "job_id": job_id,
                "token_digest": token_digest,
                "topic": topic,
                "status": "running",
                "event_sequence": 0,
                "events": [],
                "created_at_epoch": now,
                "updated_at_epoch": now,
            }
            return True

    async def load(self, job_id: str) -> dict[str, Any] | None:
        async with self._lock:
            value = self._jobs.get(job_id)
            return self._copy(value) if value is not None else None

    async def exists(self, job_id: str) -> bool:
        async with self._lock:
            return job_id in self._jobs

    async def append_event(self, job_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        async with self._lock:
            snapshot = self._jobs.get(job_id)
            if snapshot is None:
                raise KeyError(job_id)
            sequence = int(snapshot["event_sequence"]) + 1
            event = {"event_id": sequence, **payload}
            snapshot["event_sequence"] = sequence
            snapshot["events"] = [*snapshot["events"], event][-self.max_events :]
            stage = str(payload.get("stage") or "")
            snapshot["status"] = stage if stage in _TERMINAL_STAGES else "running"
            snapshot["updated_at_epoch"] = time()
            return self._copy(event)

    async def recover_interrupted(self, message: str) -> int:
        async with self._lock:
            recovered = 0
            for snapshot in self._jobs.values():
                if snapshot["status"] != "running":
                    continue
                sequence = int(snapshot["event_sequence"]) + 1
                event = {
                    "event_id": sequence,
                    "stage": "error",
                    "message": message,
                    "code": "process_restarted_during_analysis",
                }
                snapshot["event_sequence"] = sequence
                snapshot["events"] = [*snapshot["events"], event][-self.max_events :]
                snapshot["status"] = "error"
                snapshot["updated_at_epoch"] = time()
                recovered += 1
            return recovered

    async def cleanup_expired(self, cutoff_epoch: float) -> int:
        async with self._lock:
            expired = [
                job_id
                for job_id, snapshot in self._jobs.items()
                if snapshot["status"] in _TERMINAL_STAGES
                and float(snapshot["updated_at_epoch"]) < cutoff_epoch
            ]
            for job_id in expired:
                self._jobs.pop(job_id, None)
            return len(expired)

    async def delete(self, job_id: str) -> None:
        async with self._lock:
            self._jobs.pop(job_id, None)
