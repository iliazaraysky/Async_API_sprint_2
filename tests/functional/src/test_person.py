import json
import pytest
from http import HTTPStatus
from ..settings import Setting
from ..testdata.assert_data import persons_validation

Setting = Setting()


@pytest.mark.asyncio
async def test_person_index_response(create_movie_index,
                                     load_data_movies,
                                     create_person_index,
                                     make_get_request,
                                     load_data_persons,
                                     redis_pool):

    response = await make_get_request(
        Setting.ELASTICSEARCH_URL,
        request='',
        index='/persons/'
    )

    response_count = await make_get_request(
        Setting.ELASTICSEARCH_URL,
        request='_count',
        index='/persons/'
    )

    response_detail_get = await make_get_request(
        Setting.ELASTICSEARCH_URL,
        request='_doc/6f9f6eba-9322-4f21-b3f1-293efd2a9c06',
        index='/persons/'
    )

    response_fastapi_person_search = await make_get_request(
        Setting.FASTAPI_URL,
        request='/api/v1/persons/search?query=roy&page[number]=1&page[size]=5',
        index=''
    )

    search_uuid = response_fastapi_person_search.body[0][
              'uuid']
    search_full_name = response_fastapi_person_search.body[0][
              'full_name']

    response_fastapi_person_detail = await make_get_request(
        Setting.FASTAPI_URL,
        request='/api/v1/persons/6f9f6eba-9322-4f21-b3f1-293efd2a9c06',
        index=''
    )

    detail_uuid = response_fastapi_person_detail.body['uuid']
    detail_full_name = response_fastapi_person_detail.body['full_name']
    detail_film_ids = response_fastapi_person_detail.body['film_ids'][0]

    response_fastapi_person_detail_film = await make_get_request(
        Setting.FASTAPI_URL,
        request='/api/v1/persons/1c3ae50d-f79c-4c01-81fe-423006dd808c/film',
        index=''
    )

    # Создание индекса persons. Elasticsearch
    assert HTTPStatus.OK == response.status

    # Наполнение данными в индексе persons. Elasticsearch
    assert response_count.body.get('count') == persons_validation['count_elastic_index']

    # Доступность отдельного объекта. Elasticsearch
    assert response_detail_get.body['_source']['id'] == '6f9f6eba-9322-4f21-b3f1-293efd2a9c06'

    # Поиск по персонам. Параметр поиска 'Roy'
    # Сравниваем данные из Redis и Elasticsearch
    redis_data = await redis_pool.get('search_roy15', encoding='utf-8')
    redis_dict = json.loads(redis_data)
    assert redis_dict[0]['id'] == search_uuid
    assert redis_dict[0]['full_name'] == search_full_name

    # Данные по персоне
    # Сравниваем данные из Redis и Elasticsearch
    redis_data = await redis_pool.get('6f9f6eba-9322-4f21-b3f1-293efd2a9c06', encoding='utf-8')
    redis_dict = json.loads(redis_data)
    assert redis_dict['id'] == detail_uuid
    assert redis_dict['full_name'] == detail_full_name
    assert redis_dict['film_ids'][0] == detail_film_ids

    # Фильмы по персоне
    assert response_fastapi_person_detail_film.body[0]['uuid'] == 'a5b45ada-0a0a-473f-be22-e0b90e01d5d9'
    assert response_fastapi_person_detail_film.body[0]['title'] == 'Star Trek: Phoenix - Cloak & Dagger Part I'
    assert response_fastapi_person_detail_film.body[0]['imdb_rating'] == 5.6

    await redis_pool.flushall()
