import aioredis
import pytest
import aiohttp
import asyncio

from typing import Optional
from .settings import Setting
from dataclasses import dataclass
from multidict import CIMultiDictProxy
from elasticsearch import AsyncElasticsearch

from .utils.genres import load_index
from .utils.scheme import (MOVIE_SCHEME,
                           GENRE_SCHEME,
                           PERSON_SCHEME)

from .testdata.movies import MOVIES_DATA
from .testdata.genres import GENRES_DATA
from .testdata.persons import PERSONS_DATA

Setting = Setting()


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(hosts=Setting.ELASTICSEARCH_URL)
    yield client
    await client.close()


@pytest.fixture
async def redis_pool():
    pool = await aioredis.create_redis_pool(
        (Setting.REDIS_HOST, Setting.REDIS_PORT), minsize=5, maxsize=10,
    )
    yield pool
    pool.close()
    await pool.wait_closed()


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def make_get_request(session):
    async def inner(
            url: str,
            index: str = None,
            request: str = None,
            params: Optional[dict] = None) -> HTTPResponse:
        endpoint = f'http://{url}{index}{request}'
        params = params or {}
        async with session.get(endpoint, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )
    return inner


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def create_movie_index(es_client):
    await load_index(client=es_client,
                     index='movies',
                     body=MOVIE_SCHEME)
    yield
    await es_client.indices.delete(index='movies')


@pytest.fixture
async def load_data_movies(es_client):
    await es_client.bulk(body=MOVIES_DATA, doc_type='_doc', refresh=True)


@pytest.fixture
async def create_genre_index(es_client):
    await load_index(client=es_client,
                     index='genres',
                     body=GENRE_SCHEME)
    yield
    await es_client.indices.delete(index='genres')


@pytest.fixture
async def load_data_genres(es_client):
    await es_client.bulk(body=GENRES_DATA, doc_type='_doc', refresh=True)


@pytest.fixture
async def create_person_index(es_client):
    await load_index(client=es_client,
                     index='persons',
                     body=PERSON_SCHEME)
    yield
    await es_client.indices.delete(index='persons')


@pytest.fixture
async def load_data_persons(es_client):
    await es_client.bulk(body=PERSONS_DATA, doc_type='_doc', refresh=True)
