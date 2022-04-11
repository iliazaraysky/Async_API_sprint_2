from functools import lru_cache
from typing import Optional

import orjson
from aioredis import Redis
from fastapi import Depends
from elasticsearch import AsyncElasticsearch

from db.redis import get_redis
from db.elastic import get_elastic
from models.film import Film, FilmDetailView
from services.mixins import BaseDetail

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService(BaseDetail):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> Optional[FilmDetailView]:
        film = await self._from_cache(film_id)
        if not film:
            film = await self._from_elastic(film_id, 'movies', Film)
            if not film:
                return None
            await self._put_to_cache(film)
        return film

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

    async def search_films_from_elastic(self,
                                        query: str,
                                        page_number: int,
                                        page_size: int):
        data = {
            'from': page_number,
            'size': page_size,
            'query': {
                'simple_query_string': {
                    'query': query,
                    'fields': ['title^5'],
                    'default_operator': 'or'
                }
            }
        }
        films = await self.elastic.search(index='movies', body=data)
        films_list = [
            Film(**film['_source']) for film in films['hits']['hits']
        ]

        return films_list

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
            'from': page_number,
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

        films = await self.elastic.search(index='movies', body=data)
        films_list = [
            Film(**film['_source']) for film in films['hits']['hits']
        ]
        return films_list

    async def _films_list_from_cache(self, query: str):
        data = await self.redis.get(query)
        if not data:
            return None

    async def _put_films_list_to_cache(self, query: str, films):
        data = orjson.dumps([i.dict() for i in films])
        await self.redis.set(str(query),
                             data,
                             expire=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
