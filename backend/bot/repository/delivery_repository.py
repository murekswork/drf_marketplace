from repository.abc_repository import DictRepositoryImpl
from schemas.schemas import Delivery, deliveries


class DeliveryRepository(DictRepositoryImpl):
    source = None

    def __init__(self, source: dict = deliveries):
        self.source = source

    async def get(self, id: int) -> Delivery | None:
        return await super().get(id)

    async def get_all(self) -> list[Delivery] | None:
        return await super().get_all()

    async def get_by_kwargs(self, **kwargs) -> list[Delivery] | None:
        return await super().get_by_kwargs(**kwargs)

    async def add(self, delivery: Delivery) -> Delivery:
        return await super().add(delivery)

    async def update(self, id: int, **kwargs) -> Delivery:
        return await super().update(id, **kwargs)

    async def delete(self, id: int) -> Delivery:
        return await super().delete(id)
