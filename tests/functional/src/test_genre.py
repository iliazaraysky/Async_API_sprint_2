import json
import pytest
from http import HTTPStatus
from ..settings import Setting
from ..testdata.assert_data import genres_validation

Setting = Setting()


@pytest.mark.asyncio
async def test_genre_index_response(
        create_genre_index,
        make_get_request,
        load_data_genres,
        redis_pool):

    response = await make_get_request(
        Setting.ELASTICSEARCH_URL,
        request='',
        index='/genres/'
    )

    response_count = await make_get_request(
        Setting.ELASTICSEARCH_URL,
        request='_count',
        index='/genres/'
    )

    response_detail_get = await make_get_request(
        Setting.ELASTICSEARCH_URL,
        request='_doc/3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff',
        index='/genres/'
    )

    response_fastapi_genre_list = await make_get_request(
        Setting.FASTAPI_URL,
        request='/api/v1/genres',
        index=''
    )

    response_fastapi_genre_pagination = await make_get_request(
        Setting.FASTAPI_URL,
        request='/api/v1/genres?page[number]=2&page[size]=5',
        index=''
    )

    response_fastapi_genre_search = await make_get_request(
        Setting.FASTAPI_URL,
        request='/api/v1/genres/search?query=animation&page[number]=1&page[size]=1',
        index=''
    )

    search_uuid = response_fastapi_genre_search.body[0][
              'uuid']
    search_title = response_fastapi_genre_search.body[0][
              'name']

    response_fastapi_genre_by_id = await make_get_request(
        Setting.FASTAPI_URL,
        request='/api/v1/genres/6a0a479b-cfec-41ac-b520-41b2b007b611',
        index=''
    )

    # Создание индекса genres. Elasticsearch
    assert HTTPStatus.OK == response.status

    # Наполнение данными в индексе genres. Elasticsearch
    assert response_count.body.get('count') == genres_validation['count_elastic_index']

    # Доступность отдельного объекта. Elasticsearch
    assert response_detail_get.body['_source']['name'] == 'Action'

    # Список жанров
    assert (len(response_fastapi_genre_list.body)) == genres_validation['count_elastic_index']

    # Пагинация. Страница: 2. Объектов: 5
    assert (len(response_fastapi_genre_pagination.body)) == genres_validation['count_object_pagination']

    # Данные жанра
    # Сравниваем данные из Redis и Elasticsearch
    redis_data = await redis_pool.get('6a0a479b-cfec-41ac-b520-41b2b007b611', encoding='utf-8')
    redis_dict = json.loads(redis_data)
    assert redis_dict['id'] == response_fastapi_genre_by_id.body.get('uuid')
    assert redis_dict['name'] == response_fastapi_genre_by_id.body.get('name')

    # Поиск по жанрам. Параметр поиска 'animation'
    # Сравниваем данные из Redis и Elasticsearch
    redis_data = await redis_pool.get('search_animation11', encoding='utf-8')
    redis_dict = json.loads(redis_data[1:-1])
    assert redis_dict['id'] == search_uuid
    assert redis_dict['name'] == search_title

    await redis_pool.flushall()
