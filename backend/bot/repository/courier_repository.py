from repository.abc_repository import DictRepositoryImpl
from schemas.schemas import Courier, couriers


class CourierRepository(DictRepositoryImpl):
    source = couriers

    async def get(self, id: int) -> Courier | None:
        return await super().get(id)

    async def get_all(self) -> list[Courier] | None:
        return await super().get_all()

    async def get_by_kwargs(self, **kwargs) -> list[Courier] | None:
        return await super().get_by_kwargs(**kwargs)

    async def add(self, courier: Courier) -> Courier:
        return await super().add(courier)

    async def update(self, id: int, **kwargs) -> Courier:
        return await super().update(id, **kwargs)

    async def delete(self, id: int):
        return await super().delete(id)
