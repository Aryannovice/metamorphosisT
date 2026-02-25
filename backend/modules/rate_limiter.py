"""
Rate Limiter — per-IP throttling using sliding-window.
In-memory; suitable for single-instance deployment.
"""

import time
import logging
from collections import defaultdict
from threading import Lock
from typing import Tuple

logger = logging.getLogger(__name__)


class SlidingWindowRateLimiter:
    """In-memory rate limiter with sliding window per key (e.g. IP)."""

    def __init__(self, max_requests: int = 60, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._timestamps: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def is_allowed(self, key: str) -> Tuple[bool, int]:
        """
        Check if request is allowed. Returns (allowed, retry_after_seconds).
        retry_after is 0 if allowed, else seconds until next slot.
        """
        now = time.monotonic()
        cutoff = now - self.window_seconds

        with self._lock:
            ts_list = self._timestamps[key]
            # Prune old entries
            ts_list[:] = [t for t in ts_list if t > cutoff]

            if len(ts_list) < self.max_requests:
                return True, 0

            # Full — compute retry_after from oldest timestamp
            oldest = min(ts_list)
            retry_after = int(self.window_seconds - (now - oldest)) + 1
            retry_after = max(0, retry_after)
            return False, retry_after

    def record(self, key: str) -> None:
        """Record a request (call after successful allowance check)."""
        with self._lock:
            self._timestamps[key].append(time.monotonic())
