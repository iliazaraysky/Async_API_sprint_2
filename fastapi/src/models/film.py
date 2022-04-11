from uuid import UUID
from typing import List, Dict
from models.base import BaseConfig


class Film(BaseConfig):
    id: UUID
    imdb_rating: float
    genre: List[Dict[str, str]]
    title: str
    description: str
    actors: List[Dict[str, str]] = None
    writers: List[Dict[str, str]] = None
    directors: List[Dict[str, str]] = None


class FilmSearchShort(BaseConfig):
    uuid: UUID
    title: str
    imdb_rating: float


class FilmDetailView(BaseConfig):
    uuid: UUID
    title: str
    imdb_rating: float
    description: str
    genre: List[Dict[str, str]]
    actors: List[Dict[str, str]] = None
    writers: List[Dict[str, str]] = None
    directors: List[Dict[str, str]] = None
