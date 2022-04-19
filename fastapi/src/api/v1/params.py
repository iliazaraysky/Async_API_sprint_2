from pydantic import BaseSettings
from pydantic.types import PositiveInt


class PaginatedParams(BaseSettings):
    page_number: PositiveInt = 1
    page_size: PositiveInt = 50
