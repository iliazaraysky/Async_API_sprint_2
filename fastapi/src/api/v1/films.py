from http import HTTPStatus

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query

from models.film import FilmSearchShort, FilmDetailView
from services.films import FilmService, get_film_service

router = APIRouter()


@router.get('',
            response_model=List[FilmSearchShort],
            summary='Список фильмов. Сортировка по жанру и рейтенгу',
            response_description='Представление объектов в сокращенном виде')
async def film_search_and_sort(
        sort: str = 'imdb_rating',
        page_number: int = Query(1, alias='page[number]'),
        page_size: int = Query(50, alias='page[size]'),
        genre_filter: str = Query(None, alias='filter[genre]'),
        film_service: FilmService = Depends(
            get_film_service), ) -> FilmSearchShort:
    """
        Список всех объектов в категории \"Фильмы\":

        Сортировка производится по значению **imdb_rating**

        - **Номер страницы**: page[number]
        - **Колличество объектов на странице**: page[size]
        - **Фильтрация по категории**: filter[genre]

    """
    films_all = await film_service.get_films_list_search_and_sort(
        sort,
        page_number,
        page_size,
        genre_filter
    )
    films_all_results = [FilmSearchShort(
        uuid=row.id,
        title=row.title,
        imdb_rating=row.imdb_rating,
    ) for row in films_all]
    return films_all_results


@router.get('/search', response_model=List[FilmSearchShort],
            summary='Поиск по фильмам',
            response_description='Представление результатов'
                                 'поиска в сокращенном виде')
async def film_search(query: str,
                      page_number: int = Query(1, alias='page[number]'),
                      page_size: int = Query(50, alias='page[size]'),
                      film_service: FilmService = Depends(get_film_service),
                      ) -> FilmSearchShort:
    """
        Поиск по объектам в категории \"Фильмы\":

        Поиск производится по заголовку фильма **imdb_rating**

        - **Поле запроса**: query
        - **Номер страницы**: page[number]
        - **Колличество объектов на странице**: page[size]

    """
    films_all = await film_service.search_films_from_elastic(
        query,
        page_number,
        page_size
    )
    films_all_results = [FilmSearchShort(
        uuid=row.id,
        title=row.title,
        imdb_rating=row.imdb_rating
    ) for row in films_all]
    return films_all_results


@router.get(
    '/{film_id}',
    response_model=FilmDetailView,
    summary='Полное описание объекта'
)
async def film_details(
        film_id: str,
        film_service: FilmService = Depends(
            get_film_service)) -> FilmDetailView:
    """
        Полное описание объекта в категории \"Фильмы\":
    """
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Film not found'
        )
    return FilmDetailView(
        uuid=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genre=film.genre,
        actors=film.actors,
        writers=film.writers,
        directors=film.directors
    )
