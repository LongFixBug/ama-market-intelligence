from __future__ import annotations

import asyncio
import time
from collections import deque
from math import ceil


class InMemoryRateLimiter:
    """Small single-process limiter for local/dev protection.

    Production deployments must replace this with a Redis-backed limiter so
    limits are shared by all API workers and instances.
    """

    def __init__(
        self,
        max_requests: int,
        window_seconds: int,
        max_keys: int = 10_000,
    ) -> None:
        if max_requests < 1 or window_seconds < 1 or max_keys < 1:
            raise ValueError("Rate limiter settings must be positive")

        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.max_keys = max_keys
        self._requests: dict[str, deque[float]] = {}
        self._lock = asyncio.Lock()

    async def check(self, key: str) -> tuple[bool, int]:
        """Return ``(allowed, retry_after_seconds)`` for a client key."""

        now = time.monotonic()
        async with self._lock:
            timestamps = self._requests.setdefault(key, deque())
            cutoff = now - self.window_seconds
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()

            if len(timestamps) >= self.max_requests:
                retry_after = max(1, ceil(self.window_seconds - (now - timestamps[0])))
                return False, retry_after

            timestamps.append(now)
            self._evict_expired_keys(cutoff)
            return True, 0

    def _evict_expired_keys(self, cutoff: float) -> None:
        expired = [
            key
            for key, timestamps in self._requests.items()
            if not timestamps or timestamps[-1] <= cutoff
        ]
        for key in expired:
            self._requests.pop(key, None)

        while len(self._requests) > self.max_keys:
            oldest_key = min(
                self._requests,
                key=lambda key: self._requests[key][-1],
            )
            self._requests.pop(oldest_key, None)
