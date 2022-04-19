from fastapi import Depends
from functools import lru_cache

from models.genre import Genre
from db.elastic import get_elastic, AsyncStorage
from db.redis import get_redis, AsyncCacheStorage


GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class GenreService:
    def __init__(self, cache: AsyncCacheStorage, storage: AsyncStorage):
        self.cache = cache
        self.storage = storage

    async def genre_main_page(self, page_number: int, page_size: int):
        data = {
            'from': (page_number - 1) * page_size,
            'size': page_size,
            'query': {'match_all': {}}
        }
        genres = await self.storage.search(index='genres', body=data)
        genres_list = [
            Genre(**genre['_source']) for genre in genres['hits']['hits']
        ]
        return genres_list


@lru_cache()
def get_genre_service(
        cache: AsyncCacheStorage = Depends(get_redis),
        storage: AsyncStorage = Depends(get_elastic),
) -> GenreService:
    return GenreService(cache, storage)
