import json
import pytest
from http import HTTPStatus
from ..settings import Setting
from ..testdata.assert_data import films_validation

Setting = Setting()


@pytest.mark.asyncio
async def test_film_elastic_response(create_movie_index,
                                     load_data_movies,
                                     make_get_request,
                                     redis_pool
                                     ):

    response_index = await make_get_request(
        Setting.ELASTICSEARCH_URL,
        request='',
        index='/movies/'
    )

    response_count = await make_get_request(
        Setting.ELASTICSEARCH_URL,
        request='_count',
        index='/movies/'
    )

    response_detail_get = await make_get_request(
        Setting.ELASTICSEARCH_URL,
        request='_doc/00af52ec-9345-4d66-adbe-50eb917f463a',
        index='/movies/'
    )

    response_fastapi_sort = await make_get_request(
        Setting.FASTAPI_URL,
        request='/api/v1/films?sort=-imdb_rating&page[size]=5&page[number]=1',
        index=''
    )

    response_fastapi_pagination = await make_get_request(
        Setting.FASTAPI_URL,
        request='/api/v1/films?sort=-imdb_rating&page[size]=1&page[number]=5',
        index=''
    )

    response_fastapi_film_search = await make_get_request(
        Setting.FASTAPI_URL,
        request='/api/v1/films/search?query=slammer&page[number]=1&page[size]=5',
        index=''
    )

    search_uuid = response_fastapi_film_search.body[0][
              'uuid']
    search_title = response_fastapi_film_search.body[0][
              'title']

    response_fastapi_film_filter = await make_get_request(
        Setting.FASTAPI_URL,
        request='/api/v1/films?filter[genre]=3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff&sort=-imdb_rating&page[size]=5&page[number]=1',
        index=''
    )

    response_fastapi_film_detail = await make_get_request(
        Setting.FASTAPI_URL,
        request='/api/v1/films/00af52ec-9345-4d66-adbe-50eb917f463a',
        index=''
    )
    detail_uuid = response_fastapi_film_detail.body.get('uuid')
    detail_title = response_fastapi_film_detail.body.get('title')
    detail_imdb_rating = response_fastapi_film_detail.body.get('imdb_rating')
    detail_genre_id = [row['id'] for row in response_fastapi_film_detail.body.get('genre')]
    detail_actors_id = [row['id'] for row in response_fastapi_film_detail.body.get('actors')]
    detail_writers_id = [row['id'] for row in response_fastapi_film_detail.body.get('writers')]
    detail_director_name = response_fastapi_film_detail.body.get('directors')[0].get('name')

    # Создание индекса movies. Elasticsearch
    assert HTTPStatus.OK == response_index.status

    # Наполнение данными в индексе movies. Elasticsearch
    assert response_count.body.get('count') == films_validation['count_elastic_index']

    # Доступность отдельного объекта. Elasticsearch
    assert response_detail_get.body['_source']['title'] == 'Star Slammer'

    # Главная страница. Стандартная сортировка
    assert len(response_fastapi_sort.body) == films_validation['count_elastic_index']

    # Жанр и популярные фильмы в нём
    # Сравниваем данные из Redis и Elasticsearch
    redis_data = await redis_pool.get('-imdb_rating153d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff', encoding='utf-8')
    redis_dict = json.loads(redis_data)
    assert len(redis_dict) == len(response_fastapi_film_filter.body)

    # Пагинация. Категория films. Один объект на странице, пятая страница
    assert len(response_fastapi_pagination.body) == films_validation['count_object_pagination']

    # Поиск по фильмам. Параметр поиска 'Slammer'
    # Сравниваем данные из Redis и Elasticsearch
    redis_data = await redis_pool.get('search_slammer15', encoding='utf-8')
    redis_dict = json.loads(redis_data[1:-1])
    assert redis_dict['id'] == search_uuid
    assert redis_dict['title'] == search_title

    # Данные фильма
    # Сравниваем данные из Redis и Elasticsearch
    redis_data = await redis_pool.get('00af52ec-9345-4d66-adbe-50eb917f463a', encoding='utf-8')
    redis_dict = json.loads(redis_data)
    assert redis_dict['id'] == detail_uuid
    assert redis_dict['title'] == detail_title
    assert redis_dict['imdb_rating'] == detail_imdb_rating
    assert len(redis_dict['genre']) == len(detail_genre_id)
    assert len(redis_dict['actors']) == len(detail_actors_id)
    assert len(redis_dict['writers']) == len(detail_writers_id)
    assert redis_dict['directors'][0]['name'] == detail_director_name

    await redis_pool.flushall()
