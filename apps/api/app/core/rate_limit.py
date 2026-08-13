from datetime import UTC, datetime
from threading import Lock

from fastapi import HTTPException, Request

from app.core.config import settings


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._state: dict[str, list[datetime]] = {}
        self._lock = Lock()

    def check(self, key: str, limit_per_minute: int) -> None:
        now = datetime.now(UTC)
        window_start = now.replace(second=0, microsecond=0)

        with self._lock:
            bucket = self._state.setdefault(key, [])
            bucket[:] = [ts for ts in bucket if ts >= window_start]

            if len(bucket) >= limit_per_minute:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")

            bucket.append(now)


rate_limiter = InMemoryRateLimiter()


def enforce_rate_limit(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    rate_limiter.check(client_ip, settings.api_rate_limit_per_minute)
