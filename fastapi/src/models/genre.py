from uuid import UUID
from models.base import BaseConfig


class Genre(BaseConfig):
    id: UUID
    name: str


class GenresList(BaseConfig):
    uuid: UUID
    name: str


class GenreDetail(BaseConfig):
    uuid: UUID
    name: str
