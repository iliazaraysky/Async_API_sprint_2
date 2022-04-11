from uuid import UUID
from typing import List
from models.base import BaseConfig


class Person(BaseConfig):
    id: UUID
    full_name: str
    role: List[str]
    film_ids: List[str] = None


class PersonSearch(BaseConfig):
    uuid: UUID
    full_name: str
    role: List[str]
    film_ids: List[str] = None


class PersonDetail(BaseConfig):
    uuid: UUID
    full_name: str
    role: List[str]
    film_ids: List[str] = None
