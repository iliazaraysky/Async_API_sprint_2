from http import HTTPStatus

from typing import List
from fastapi import APIRouter, Depends, HTTPException

from models.genre import GenresList, GenreDetail
from services.genre import GenreService, get_genre_service

router = APIRouter()


@router.get('', response_model=List[GenresList],
            summary='Список жанров',
            response_description='Представление объектов в сокращенном виде')
async def genre_main_page(
        genre_service: GenreService = Depends(get_genre_service)
) -> GenresList:
    """
        Список всех объектов в категории \"Жанры\":
    """
    genres_all = await genre_service.genre_main_page()
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


@router.get('/{genre_id}', response_model=GenreDetail,
            summary='Полное описание жанра',
            response_description='Представление объектов в сокращенном виде')
async def genre_details(
        genre_id: str,
        genre_service: GenreService = Depends(get_genre_service)
) -> GenreDetail:

    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Genre not found'
        )
    return GenreDetail(uuid=genre.id, name=genre.name)
