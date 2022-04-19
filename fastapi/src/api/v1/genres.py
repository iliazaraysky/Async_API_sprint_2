from typing import List
from http import HTTPStatus
from .params import PaginatedParams
from models.genre import GenresList, GenreDetail, Genre
from services.genre import GenreService, get_genre_service
from fastapi import APIRouter, Depends, HTTPException, Query

from services.base import BaseDetail, BaseSearch
from services.base import get_service, get_service_search

router = APIRouter()


@router.get('', response_model=List[GenresList],
            summary='Список жанров',
            response_description='Представление объектов в сокращенном виде')
async def genre_main_page(
        page_number: int = Query(PaginatedParams().page_number, alias='page[number]'),
        page_size: int = Query(PaginatedParams().page_size, alias='page[size]'),
        genre_service: GenreService = Depends(get_genre_service)
) -> GenresList:
    """
        Список всех объектов в категории \"Жанры\":
    """
    genres_all = await genre_service.genre_main_page(page_number, page_size)
    if not genres_all:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Genres not found'
        )
    genres_all_list = [GenresList(
        uuid=row.id,
        name=row.name
    ) for row in genres_all]
    return genres_all_list


@router.get('/search', response_model=List[GenresList],
            summary='Поиск по жанрам',
            response_description='Представление результатов'
                                 'поиска в сокращенном виде')
async def genre_search(query: str,
                      page_number: int = Query(PaginatedParams().page_number, alias='page[number]'),
                      page_size: int = Query(PaginatedParams().page_size, alias='page[size]'),
                      genre_service: BaseSearch = Depends(get_service_search),
                      ) -> GenresList:
    """
        Поиск по объектам в категории \"Жанры\":

        Поиск производится по заголовку жанра

        - **Поле запроса**: query
        - **Номер страницы**: page[number]
        - **Колличество объектов на странице**: page[size]

    """
    genre_search = await genre_service.get_search_result_from_elastic(
        query,
        page_number,
        page_size,
        ['name', 'id'],
        'genres',
        Genre
    )
    genre_search_results = [GenresList(
        uuid=row.id,
        name=row.name
    ) for row in genre_search]
    return genre_search_results


@router.get('/{genre_id}', response_model=GenreDetail,
            summary='Полное описание жанра',
            response_description='Представление объектов в сокращенном виде')
async def genre_details(
        genre_id: str,
        genre_service: BaseDetail = Depends(get_service)) -> GenreDetail:

    genre = await genre_service.get_by_id(genre_id, 'genres', Genre)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Genre not found'
        )
    return GenreDetail(uuid=genre.id, name=genre.name)
