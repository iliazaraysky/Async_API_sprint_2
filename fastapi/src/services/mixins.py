import elasticsearch.exceptions

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class BaseDetail:
    async def _from_elastic(self, object_id: str, _index: str, _dataclass):
        try:
            doc = await self.elastic.get(_index, object_id)
        except elasticsearch.exceptions.NotFoundError:
            return None
        return _dataclass(**doc['_source'])

    async def _put_to_cache(self, data):
        await self.redis.set(
            str(data.id),
            data.json(),
            expire=FILM_CACHE_EXPIRE_IN_SECONDS
        )

    async def _from_cache(self, object_id: str):
        data = await self.redis.get(object_id)
        if not data:
            return None
