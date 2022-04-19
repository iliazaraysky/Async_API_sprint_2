from typing import List
from http import HTTPStatus
from .params import PaginatedParams
from models.film import FilmSearchShort
from models.person import PersonSearch, PersonDetail, Person
from fastapi import APIRouter, Depends, HTTPException, Query
from services.person import PersonService, get_person_service

from services.base import BaseDetail, BaseSearch
from services.base import get_service, get_service_search

router = APIRouter()


@router.get('/search', response_model=List[PersonSearch],
            summary='Поиск по персонам',
            response_description='Представление результатов'
                                 'поиска в сокращенном виде')
async def person_search(
        query: str,
        page_number: int = Query(PaginatedParams().page_number, alias='page[number]'),
        page_size: int = Query(PaginatedParams().page_size, alias='page[size]'),
        person_service: BaseSearch = Depends(get_service_search),) -> PersonSearch:
    """
        Поиск по объектам в категории \"Персоны\":

        Поиск производится по имени **full_name**

        - **Поле запроса**: query
        - **Номер страницы**: page[number]
        - **Колличество объектов на странице**: page[size]
    """
    persons_all = await person_service.get_search_result_from_elastic(
        query,
        page_number,
        page_size,
        ['full_name'],
        'persons',
        Person
    )
    persons_all_results = [PersonSearch(
        uuid=row.id,
        full_name=row.full_name,
        role=row.role,
        film_ids=row.film_ids
    ) for row in persons_all]
    return persons_all_results


@router.get('/{person_id}', response_model=PersonDetail,
            summary='Полное описание объекта')
async def film_details(
        person_id: str,
        person_service: BaseDetail = Depends(get_service)
) -> PersonDetail:
    """
        Полное описание объекта в категории \"Персоны\":
    """
    person = await person_service.get_by_id(person_id, 'persons', Person)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='Person not found')
    return PersonDetail(
        uuid=person.id,
        full_name=person.full_name,
        role=person.role,
        film_ids=person.film_ids,
    )


@router.get('/{person_id}/film',
            response_model=List[FilmSearchShort],
            summary='Фильмы в которых учавствует персона')
async def person_film(
        person_id: str,
        person_service: PersonService = Depends(get_person_service)
) -> FilmSearchShort:
    films = await person_service.person_films_from_elastic(person_id)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='Films not found')
    films_all_results = [FilmSearchShort(
        uuid=row.id,
        title=row.title,
        imdb_rating=row.imdb_rating) for row in films]
    return films_all_results
