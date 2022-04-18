from functools import lru_cache
from typing import Optional

import orjson
from aioredis import Redis
from fastapi import Depends
from elasticsearch import AsyncElasticsearch

from db.redis import get_redis
from db.elastic import get_elastic
from models.genre import Genre
from services.mixins import BaseDetail


GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class GenreService(BaseDetail):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def genre_main_page(self, page_number: int, page_size: int):
        data = {
            'from': (page_number - 1) * page_size,
            'size': page_size,
            'query': {'match_all': {}}
        }
        genres = await self.elastic.search(index='genres', body=data)
        genres_list = [
            Genre(**genre['_source']) for genre in genres['hits']['hits']
        ]
        return genres_list

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        genre = await self._from_cache(genre_id)
        if not genre:
            genre = await self._from_elastic(genre_id, 'genres', Genre)
            if not genre:
                return None
            await self._put_to_cache(genre)
        return genre

    async def get_search_result_from_elastic(
            self,
            query: str,
            page_number: int,
            page_size: int
    ):
        query_redis = ('search_genre' + str(query) + str(page_number) + str(page_size))
        genres = await self._genre_list_from_cache(query_redis)
        if not genres:
            genres = await self.search_genre_from_elastic(
                query,
                page_number,
                page_size
            )
            if not genres:
                return None
            await self._put_genre_list_to_cache(query_redis, genres)
        return genres

    async def search_genre_from_elastic(
            self,
            query: str,
            page_number: int,
            page_size: int
    ):

        data = {
            'from': (page_number - 1) * page_size,
            'size': page_size,
            'query': {
                'simple_query_string': {
                    'query': query,
                    'fields': ['name', 'id'],
                    'default_operator': 'or'
                }
            }
        }

        genres = await self.elastic.search(index='genres', body=data)
        genre_list = [
            Genre(**genre['_source']) for genre in genres['hits']['hits']
        ]

        return genre_list

    async def _genre_list_from_cache(self, query: str):
        data = await self.redis.get(query)
        if not data:
            return None

    async def _put_genre_list_to_cache(self, query: str, films):
        data = orjson.dumps([i.dict() for i in films])
        await self.redis.set(str(query),
                             data,
                             expire=GENRE_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
