from __future__ import annotations

import asyncio
import json
import sqlite3
from pathlib import Path
from time import time
from typing import Any, Protocol


class CampaignStore(Protocol):
    """Durable state contract for campaign coordination.

    The service only depends on this small interface so SQLite can be used for
    a local/single-host deployment and replaced by a transactional
    Postgres/Redis adapter without changing the agent or API contract.
    """

    async def save(self, campaign_id: str, snapshot: dict[str, Any]) -> None: ...

    async def load(self, campaign_id: str) -> dict[str, Any] | None: ...

    async def list_recoverable(self) -> list[dict[str, Any]]: ...

    async def count(self) -> int: ...

    async def cleanup_expired(self, cutoff_epoch: float) -> None: ...

    async def reserve_content(self, platform: str, content_hash: str, expires_at: float) -> bool: ...

    async def release_content(self, platform: str, content_hash: str, expires_at: float) -> None: ...

    async def acquire_lease(self, campaign_id: str, owner_id: str, expires_at: float) -> bool: ...

    async def release_lease(self, campaign_id: str, owner_id: str) -> None: ...

    async def lease_active(self, campaign_id: str) -> bool: ...

    async def release_owner(self, owner_id: str) -> None: ...


class SQLiteCampaignStore:
    """Small durable store with WAL and short-lived transactional writes.

    SQLite is intentionally the local default, not a claim of distributed
    locking. For multiple application instances use the same contract with a
    Postgres/Redis implementation and shared pub/sub for live SSE fan-out.
    """

    def __init__(self, path: str | Path):
        self.path = str(path)
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
                CREATE TABLE IF NOT EXISTS campaign_snapshots (
                    campaign_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    last_access_epoch REAL NOT NULL,
                    updated_at_epoch REAL NOT NULL,
                    payload TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_campaign_snapshots_recovery
                    ON campaign_snapshots(status);
                CREATE TABLE IF NOT EXISTS content_reservations (
                    platform TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    expires_at REAL NOT NULL,
                    PRIMARY KEY(platform, content_hash)
                );
                CREATE INDEX IF NOT EXISTS idx_content_reservations_expiry
                    ON content_reservations(expires_at);
                CREATE TABLE IF NOT EXISTS campaign_leases (
                    campaign_id TEXT PRIMARY KEY,
                    owner_id TEXT NOT NULL,
                    expires_at REAL NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_campaign_leases_expiry
                    ON campaign_leases(expires_at);
                """
            )
            connection.commit()
        finally:
            connection.close()

    async def save(self, campaign_id: str, snapshot: dict[str, Any]) -> None:
        await asyncio.to_thread(self._save_sync, campaign_id, snapshot)

    def _save_sync(self, campaign_id: str, snapshot: dict[str, Any]) -> None:
        campaign = snapshot.get("campaign") or {}
        status = str(campaign.get("status") or "drafting")
        last_access_epoch = float(snapshot.get("last_access_epoch") or time())
        payload = json.dumps(snapshot, ensure_ascii=False, separators=(",", ":"))
        now = time()
        connection = self._connect()
        try:
            connection.execute(
                """
                INSERT INTO campaign_snapshots
                    (campaign_id, status, last_access_epoch, updated_at_epoch, payload)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(campaign_id) DO UPDATE SET
                    status=excluded.status,
                    last_access_epoch=excluded.last_access_epoch,
                    updated_at_epoch=excluded.updated_at_epoch,
                    payload=excluded.payload
                """,
                (campaign_id, status, last_access_epoch, now, payload),
            )
            connection.commit()
        finally:
            connection.close()

    async def load(self, campaign_id: str) -> dict[str, Any] | None:
        return await asyncio.to_thread(self._load_sync, campaign_id)

    def _load_sync(self, campaign_id: str) -> dict[str, Any] | None:
        connection = self._connect()
        try:
            row = connection.execute(
                "SELECT payload FROM campaign_snapshots WHERE campaign_id = ?",
                (campaign_id,),
            ).fetchone()
            return json.loads(row["payload"]) if row else None
        finally:
            connection.close()

    async def list_recoverable(self) -> list[dict[str, Any]]:
        return await asyncio.to_thread(self._list_recoverable_sync)

    def _list_recoverable_sync(self) -> list[dict[str, Any]]:
        connection = self._connect()
        try:
            rows = connection.execute(
                """
                SELECT payload
                FROM campaign_snapshots
                WHERE status IN ('scheduled', 'publishing')
                ORDER BY updated_at_epoch ASC
                """
            ).fetchall()
            return [json.loads(row["payload"]) for row in rows]
        finally:
            connection.close()

    async def count(self) -> int:
        return await asyncio.to_thread(self._count_sync)

    def _count_sync(self) -> int:
        connection = self._connect()
        try:
            row = connection.execute("SELECT COUNT(*) AS total FROM campaign_snapshots").fetchone()
            return int(row["total"])
        finally:
            connection.close()

    async def cleanup_expired(self, cutoff_epoch: float) -> None:
        await asyncio.to_thread(self._cleanup_expired_sync, cutoff_epoch)

    def _cleanup_expired_sync(self, cutoff_epoch: float) -> None:
        connection = self._connect()
        try:
            connection.execute(
                """
                DELETE FROM campaign_snapshots
                WHERE status IN ('completed', 'needs_review', 'failed', 'cancelled')
                  AND last_access_epoch < ?
                """,
                (cutoff_epoch,),
            )
            connection.execute("DELETE FROM content_reservations WHERE expires_at <= ?", (time(),))
            connection.commit()
        finally:
            connection.close()

    async def reserve_content(self, platform: str, content_hash: str, expires_at: float) -> bool:
        return await asyncio.to_thread(self._reserve_content_sync, platform, content_hash, expires_at)

    def _reserve_content_sync(self, platform: str, content_hash: str, expires_at: float) -> bool:
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("DELETE FROM content_reservations WHERE expires_at <= ?", (time(),))
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO content_reservations(platform, content_hash, expires_at)
                VALUES (?, ?, ?)
                """,
                (platform, content_hash, expires_at),
            )
            connection.commit()
            return cursor.rowcount == 1
        finally:
            connection.close()

    async def release_content(self, platform: str, content_hash: str, expires_at: float) -> None:
        await asyncio.to_thread(self._release_content_sync, platform, content_hash, expires_at)

    def _release_content_sync(self, platform: str, content_hash: str, expires_at: float) -> None:
        connection = self._connect()
        try:
            connection.execute(
                """
                DELETE FROM content_reservations
                WHERE platform = ? AND content_hash = ? AND expires_at = ?
                """,
                (platform, content_hash, expires_at),
            )
            connection.commit()
        finally:
            connection.close()

    async def acquire_lease(self, campaign_id: str, owner_id: str, expires_at: float) -> bool:
        return await asyncio.to_thread(self._acquire_lease_sync, campaign_id, owner_id, expires_at)

    def _acquire_lease_sync(self, campaign_id: str, owner_id: str, expires_at: float) -> bool:
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("DELETE FROM campaign_leases WHERE expires_at <= ?", (time(),))
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO campaign_leases(campaign_id, owner_id, expires_at)
                VALUES (?, ?, ?)
                """,
                (campaign_id, owner_id, expires_at),
            )
            connection.commit()
            return cursor.rowcount == 1
        finally:
            connection.close()

    async def release_lease(self, campaign_id: str, owner_id: str) -> None:
        await asyncio.to_thread(self._release_lease_sync, campaign_id, owner_id)

    def _release_lease_sync(self, campaign_id: str, owner_id: str) -> None:
        connection = self._connect()
        try:
            connection.execute(
                "DELETE FROM campaign_leases WHERE campaign_id = ? AND owner_id = ?",
                (campaign_id, owner_id),
            )
            connection.commit()
        finally:
            connection.close()

    async def lease_active(self, campaign_id: str) -> bool:
        return await asyncio.to_thread(self._lease_active_sync, campaign_id)

    def _lease_active_sync(self, campaign_id: str) -> bool:
        connection = self._connect()
        try:
            row = connection.execute(
                "SELECT expires_at FROM campaign_leases WHERE campaign_id = ?",
                (campaign_id,),
            ).fetchone()
            return bool(row and float(row["expires_at"]) > time())
        finally:
            connection.close()

    async def release_owner(self, owner_id: str) -> None:
        await asyncio.to_thread(self._release_owner_sync, owner_id)

    def _release_owner_sync(self, owner_id: str) -> None:
        connection = self._connect()
        try:
            connection.execute("DELETE FROM campaign_leases WHERE owner_id = ?", (owner_id,))
            connection.commit()
        finally:
            connection.close()


class InMemoryCampaignStore:
    """Non-durable store for isolated unit tests and ephemeral previews."""

    def __init__(self):
        self._snapshots: dict[str, dict[str, Any]] = {}
        self._reservations: dict[tuple[str, str], float] = {}
        self._leases: dict[str, tuple[str, float]] = {}
        self._lock = asyncio.Lock()

    @staticmethod
    def _copy(snapshot: dict[str, Any]) -> dict[str, Any]:
        return json.loads(json.dumps(snapshot, ensure_ascii=False))

    async def save(self, campaign_id: str, snapshot: dict[str, Any]) -> None:
        async with self._lock:
            self._snapshots[campaign_id] = self._copy(snapshot)

    async def load(self, campaign_id: str) -> dict[str, Any] | None:
        async with self._lock:
            snapshot = self._snapshots.get(campaign_id)
            return self._copy(snapshot) if snapshot is not None else None

    async def list_recoverable(self) -> list[dict[str, Any]]:
        async with self._lock:
            return [
                self._copy(snapshot)
                for snapshot in self._snapshots.values()
                if (snapshot.get("campaign") or {}).get("status") in {"scheduled", "publishing"}
            ]

    async def count(self) -> int:
        async with self._lock:
            return len(self._snapshots)

    async def cleanup_expired(self, cutoff_epoch: float) -> None:
        async with self._lock:
            expired_ids = [
                campaign_id
                for campaign_id, snapshot in self._snapshots.items()
                if (snapshot.get("campaign") or {}).get("status")
                in {"completed", "needs_review", "failed", "cancelled"}
                and float(snapshot.get("last_access_epoch") or 0) < cutoff_epoch
            ]
            for campaign_id in expired_ids:
                self._snapshots.pop(campaign_id, None)
            now = time()
            self._reservations = {
                key: expiry for key, expiry in self._reservations.items() if expiry > now
            }

    async def reserve_content(self, platform: str, content_hash: str, expires_at: float) -> bool:
        async with self._lock:
            now = time()
            self._reservations = {
                key: expiry for key, expiry in self._reservations.items() if expiry > now
            }
            key = (platform, content_hash)
            if key in self._reservations:
                return False
            self._reservations[key] = expires_at
            return True

    async def release_content(self, platform: str, content_hash: str, expires_at: float) -> None:
        async with self._lock:
            key = (platform, content_hash)
            if self._reservations.get(key) == expires_at:
                self._reservations.pop(key, None)

    async def acquire_lease(self, campaign_id: str, owner_id: str, expires_at: float) -> bool:
        async with self._lock:
            now = time()
            self._leases = {
                key: lease for key, lease in self._leases.items() if lease[1] > now
            }
            if campaign_id in self._leases:
                return False
            self._leases[campaign_id] = (owner_id, expires_at)
            return True

    async def release_lease(self, campaign_id: str, owner_id: str) -> None:
        async with self._lock:
            lease = self._leases.get(campaign_id)
            if lease is not None and lease[0] == owner_id:
                self._leases.pop(campaign_id, None)

    async def lease_active(self, campaign_id: str) -> bool:
        async with self._lock:
            lease = self._leases.get(campaign_id)
            if lease is None:
                return False
            if lease[1] <= time():
                self._leases.pop(campaign_id, None)
                return False
            return True

    async def release_owner(self, owner_id: str) -> None:
        async with self._lock:
            self._leases = {
                campaign_id: lease
                for campaign_id, lease in self._leases.items()
                if lease[0] != owner_id
            }
