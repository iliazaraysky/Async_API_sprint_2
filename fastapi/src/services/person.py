from functools import lru_cache
from typing import Optional

import orjson
from aioredis import Redis
from fastapi import Depends
from elasticsearch import AsyncElasticsearch

from db.redis import get_redis
from db.elastic import get_elastic
from models.person import Person
from models.film import Film
from services.mixins import BaseDetail


PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService(BaseDetail):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self._from_cache(person_id)
        if not person:
            person = await self._from_elastic(person_id, 'persons', Person)
            if not person:
                return None
            await self._put_to_cache(person)
        return person

    async def get_search_result_from_elastic(
            self,
            query: str,
            page_number: int,
            page_size: int
    ):
        query_redis = ('search_person_' + str(query) + str(page_number) + str(page_size))
        persons = await self._person_list_from_cache(query_redis)
        if not persons:
            persons = await self.search_persons_from_elastic(
                query,
                page_number,
                page_size
            )
            if not persons:
                return None
            await self._put_person_list_to_cache(query_redis, persons)
        return persons

    async def search_persons_from_elastic(
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
                    'fields': ['full_name'],
                    'default_operator': 'or'
                }
            }
        }
        persons = await self.elastic.search(index='persons', body=data)
        persons_list = [
            Person(**person['_source']) for person in persons['hits']['hits']
        ]

        return persons_list

    async def person_films_from_elastic(self, person_id: str):
        doc = await self.elastic.get('persons', person_id)
        doc_list = doc['_source']['film_ids']
        data = {
            'query': {
                'ids': {
                    'values': doc_list
                }
            }
        }
        films = await self.elastic.search(index='movies', body=data)
        films_list = [
            Film(**film['_source']) for film in films['hits']['hits']
        ]
        return films_list

    async def _person_list_from_cache(self, query: str):
        data = await self.redis.get(query)
        if not data:
            return None

    async def _put_person_list_to_cache(self, query: str, films):
        data = orjson.dumps([i.dict() for i in films])
        await self.redis.set(str(query),
                             data,
                             expire=PERSON_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
