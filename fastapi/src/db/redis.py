from typing import Optional
from aioredis import Redis
from abc import ABC, abstractmethod

redis: Optional[Redis] = None


async def get_redis() -> Redis:
    return redis


class AsyncCacheStorage(ABC):
    @abstractmethod
    async def get(self, key: str, **kwargs):
        pass

    @abstractmethod
    async def set(self, key: str, value: str, expire: int, **kwargs):
        pass
