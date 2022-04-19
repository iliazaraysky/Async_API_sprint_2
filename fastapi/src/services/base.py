import orjson
from fastapi import Depends
import elasticsearch.exceptions
from functools import lru_cache

from db.redis import get_redis, AsyncCacheStorage
from db.elastic import get_elastic, AsyncStorage


CACHE_EXPIRE_IN_SECONDS = 60 * 5


class Connection:
    def __init__(self, cache: AsyncCacheStorage, storage: AsyncStorage):
        self.cache: AsyncCacheStorage = cache
        self.storage: AsyncStorage = storage


class BaseDetail(Connection):
    async def get_by_id(self, obj_id: str, index: str, dataclass):
        data = await self._from_cache(obj_id)
        if not data:
            data = await self._from_elastic(obj_id, index, dataclass)
            if not data:
                return None
            await self._put_to_cache(data)
        return data

    async def _from_elastic(self, object_id: str, _index: str, _dataclass):
        try:
            doc = await self.storage.get(_index, object_id)
        except elasticsearch.exceptions.NotFoundError:
            return None
        return _dataclass(**doc['_source'])

    async def _put_to_cache(self, data):
        await self.cache.set(
            str(data.id),
            data.json(),
            expire=CACHE_EXPIRE_IN_SECONDS
        )

    async def _from_cache(self, object_id: str):
        data = await self.cache.get(object_id)
        if not data:
            return None


@lru_cache()
def get_service(
        cache: AsyncCacheStorage = Depends(get_redis),
        storage: AsyncStorage = Depends(get_elastic),
) -> BaseDetail:
    return BaseDetail(cache, storage)


class BaseSearch(Connection):
    async def search_from_elastic(self,
                                  query: str,
                                  page_number: int,
                                  page_size: int,
                                  _fields: list,
                                  _index: str,
                                  _dataclass):

        data = {
            'from': (page_number - 1) * page_size,
            'size': page_size,
            'query': {
                'simple_query_string': {
                    'query': query,
                    'fields': _fields,
                    'default_operator': 'or'
                }
            }
        }

        films = await self.storage.search(index=_index, body=data)
        films_list = [
            _dataclass(**film['_source']) for film in films['hits']['hits']
        ]

        return films_list

    async def get_search_result_from_elastic(
            self,
            query: str,
            page_number: int,
            page_size: int,
            fields: list,
            _index: str,
            _dataclass
    ):
        query_redis = ('search_' + str(query) + str(page_number) + str(page_size))
        datas = await self._films_list_from_cache(query_redis)
        if not datas:
            datas = await self.search_from_elastic(
                query,
                page_number,
                page_size,
                fields,
                _index,
                _dataclass
            )
            if not datas:
                return None
            await self._put_films_list_to_cache(query_redis, datas)
        return datas

    async def _films_list_from_cache(self, query: str):
        data = await self.cache.get(query)
        if not data:
            return None

    async def _put_films_list_to_cache(self, query: str, films):
        data = orjson.dumps([i.dict() for i in films])
        await self.cache.set(str(query),
                             data,
                             expire=CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_service_search(
        cache: AsyncCacheStorage = Depends(get_redis),
        storage: AsyncStorage = Depends(get_elastic),
) -> BaseSearch:
    return BaseSearch(cache, storage)
