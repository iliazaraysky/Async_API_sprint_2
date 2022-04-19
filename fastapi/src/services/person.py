import orjson
from fastapi import Depends
from models.film import Film
from functools import lru_cache
from db.elastic import get_elastic, AsyncStorage
from db.redis import get_redis, AsyncCacheStorage

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService:
    def __init__(self, cache: AsyncCacheStorage, storage: AsyncStorage):
        self.cache = cache
        self.elastic = storage

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
        data = await self.cache.get(query)
        if not data:
            return None

    async def _put_person_list_to_cache(self, query: str, films):
        data = orjson.dumps([i.dict() for i in films])
        await self.cache.set(str(query),
                             data,
                             expire=PERSON_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_person_service(
        cache: AsyncCacheStorage = Depends(get_redis),
        storage: AsyncStorage = Depends(get_elastic),
) -> PersonService:
    return PersonService(cache, storage)
