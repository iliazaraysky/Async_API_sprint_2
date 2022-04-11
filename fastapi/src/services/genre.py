from functools import lru_cache
from typing import Optional

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

    async def genre_main_page(self):
        genres = await self.elastic.search(index='genres')
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


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
