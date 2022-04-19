from functools import lru_cache

import orjson
from fastapi import Depends

from models.film import Film, FilmDetailView
from db.elastic import get_elastic, AsyncStorage
from db.redis import get_redis, AsyncCacheStorage


FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService:
    def __init__(self, cache: AsyncCacheStorage, storage: AsyncStorage):
        self.cache: AsyncCacheStorage = cache
        self.storage: AsyncStorage = storage

    async def get_films_list_search_and_sort(self,
                                             sort: str,
                                             page_number: int,
                                             page_size: int,
                                             genre_filter: str):
        query = (str(sort) + str(page_number) + str(page_size) + str(genre_filter))
        films = await self._films_list_from_cache(query)
        if not films:
            films = await self.search_and_sort_films_from_elastic(
                sort,
                page_number,
                page_size,
                genre_filter
            )
            if not films:
                return None
            await self._put_films_list_to_cache(query, films)
        return films

    async def search_and_sort_films_from_elastic(self,
                                                 sort: str,
                                                 page_number: int,
                                                 page_size: int,
                                                 genre_filter: str):
        sort_param = 'asc'
        if sort.startswith('-'):
            sort = sort[1:]
            sort_param = 'desc'

        data = {
            'from': (page_number - 1) * page_size,
            'size': page_size,
            'sort': [
                {
                    sort: {'order': sort_param}
                }
            ]
        }

        if genre_filter:
            data['query'] = {
                'bool': {
                    'filter': {
                        'nested': {
                            'path': 'genre',
                            'query': {
                                'term': {'genre.id': genre_filter}
                            }
                        }
                    }
                }
            }

        films = await self.storage.search(index='movies', body=data)
        films_list = [
            Film(**film['_source']) for film in films['hits']['hits']
        ]
        return films_list

    async def _films_list_from_cache(self, query: str):
        data = await self.cache.get(query)
        if not data:
            return None

    async def _put_films_list_to_cache(self, query: str, films):
        data = orjson.dumps([i.dict() for i in films])
        await self.cache.set(str(query),
                             data,
                             expire=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
        cache: AsyncCacheStorage = Depends(get_redis),
        storage: AsyncStorage = Depends(get_elastic),
) -> FilmService:
    return FilmService(cache, storage)
