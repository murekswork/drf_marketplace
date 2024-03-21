from abc import ABC, abstractmethod
from typing import Any, Generator

from schemas.schemas import Delivery


class DeliveryManagerAbc(ABC):

    @abstractmethod
    async def get_delivery(self, id):
        raise NotImplementedError

    @abstractmethod
    async def get_undelivered_deliveries(self):
        raise NotImplementedError

    @abstractmethod
    async def get_delivery_status(self, id):
        raise NotImplementedError

    @abstractmethod
    async def get_delivery_courier(self, id):
        raise NotImplementedError

    @abstractmethod
    async def cancel_delivery(self, id):
        raise NotImplementedError

    @abstractmethod
    async def accept_delivery(self, id, courier_id):
        raise NotImplementedError

    @abstractmethod
    async def finish_delivery(self, id: int, status: int) -> Delivery | None:
        raise NotImplementedError

    @abstractmethod
    async def add_delivery(self, delivery: Delivery):
        raise NotImplementedError


class DeliveryManagerImpl(DeliveryManagerAbc):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def get_undelivered_deliveries(self) -> Generator[Delivery, Any, None]:
        from schemas.schemas import deliveries

        # Method to get all undelivered deliveries.
        d = (deliveries[k] for k in deliveries if deliveries[k].status == 1)
        return d

    async def get_delivery(self, id: int) -> Delivery | None:
        from schemas.schemas import deliveries
        d = deliveries.get(id, None)
        return d

    async def get_delivery_status(self, id: int) -> int | None:
        d = await self.get_delivery(id)
        if d is not None:
            return d.status
        return None

    async def get_delivery_courier(self, id) -> int | None:
        d = await self.get_delivery(id)
        if d is not None:
            return d.courier
        return None

    async def cancel_delivery(self, id):
        d = await self.get_delivery(id)
        d.status = 'cancelled'

    async def accept_delivery(self, id, courier_id: int) -> None:
        d = await self.get_delivery(id)
        if d is not None:
            d.courier = courier_id
            d.status = 3

    async def finish_delivery(self, id: int, status: int) -> Delivery | None:
        d = await self.get_delivery(id)
        if d:
            d.status = status
        return d

    async def add_delivery(self, delivery: Delivery):
        from schemas.schemas import deliveries
        deliveries[delivery.id] = delivery
