from abc import ABC, abstractmethod

from schemas.schemas import Courier


class RepositoryAbc(ABC):

    @abstractmethod
    async def get(self, id):
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list | None:
        raise NotImplementedError

    @abstractmethod
    async def add(self, obj):
        raise NotImplementedError

    @abstractmethod
    async def update(self, id, fields):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id):
        raise NotImplementedError


class CourierRepositoryAbc(RepositoryAbc):

    @abstractmethod
    async def get_free_couriers(self) -> list[Courier]:
        raise NotImplementedError

    # @abstractmethod
    # async def get_nearest_free_courier(self, delivery: Delivery) -> Courier | None:
    #     raise NotImplementedError

    @abstractmethod
    async def lock_courier(self, id: int):
        raise NotImplementedError

    @abstractmethod
    async def unlock_courier(self, id: int):
        raise NotImplementedError


class DictRepositoryImpl(RepositoryAbc):
    source: dict | None = None

    async def get(self, id):
        return self.source.get(id, None)

    async def get_all(self) -> list | None:
        if self.source:
            return [obj for obj in self.source.values()]
        return None

    async def get_by_kwargs(self, **kwargs):
        return [obj for obj in self.source.values() if
                all(hasattr(obj, kwarg) and getattr(obj, kwarg) == value for kwarg, value in kwargs.items())]

    async def add(self, obj):
        self.source[obj.id] = obj
        return obj

    async def update(self, id, **kwargs):
        obj = self.source.get(id, None)
        if obj:
            obj.__dict__.update(**kwargs)
        return obj

    async def delete(self, id):
        return self.source.pop(id)
