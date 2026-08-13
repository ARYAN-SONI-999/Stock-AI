import json
from collections.abc import Callable

from redis.asyncio import Redis

from app.core.config import settings


class CacheClient:
    def __init__(self) -> None:
        self._client: Redis | None = None

    def _get_client(self) -> Redis:
        if self._client is None:
            self._client = Redis.from_url(settings.redis_url, decode_responses=True)
        return self._client

    async def get_json(self, key: str) -> dict | None:
        try:
            value = await self._get_client().get(key)
            return json.loads(value) if value else None
        except Exception:
            return None

    async def set_json(self, key: str, payload: dict, ttl_seconds: int) -> None:
        try:
            await self._get_client().set(key, json.dumps(payload, default=str), ex=ttl_seconds)
        except Exception:
            return


cache_client = CacheClient()
