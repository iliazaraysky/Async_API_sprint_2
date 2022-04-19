from typing import Optional
from abc import ABC, abstractmethod
from elasticsearch import AsyncElasticsearch

es: Optional[AsyncElasticsearch] = None


async def get_elastic() -> AsyncElasticsearch:
    return es


class AsyncStorage(ABC):
    @abstractmethod
    async def get(self, _index: str, object_id: str, **kwargs):
        pass

    @abstractmethod
    async def search(self, _index: str, data, **kwargs):
        pass
