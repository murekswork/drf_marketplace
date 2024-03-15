from abc import ABC, abstractmethod
from typing import Any, Generator

from courier.schemas import Delivery


class DeliveryService(ABC):

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
    async def finish_delivery(self, id) -> Delivery:
        raise NotImplementedError

    @abstractmethod
    async def add_delivery(self, delivery: Delivery):
        raise NotImplementedError


class DeliveryServiceImpl(DeliveryService):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def get_undelivered_deliveries(self) -> Generator[Delivery, Any, None]:
        from courier.src.service import deliveries

        # Method to get all undelivered deliveries.
        d = (deliveries[k] for k in deliveries if deliveries[k].status == 'searching')
        return d

    async def get_delivery(self, id: str) -> Delivery | None:
        from courier.src.service import deliveries

        d = deliveries.get(id, None)
        return d

    async def get_delivery_status(self, id: str) -> str | None:
        d = await self.get_delivery(id)
        if d is not None:
            return d.status
        return None

    async def get_delivery_courier(self, id) -> str | None:
        d = await self.get_delivery(id)
        if d is not None:
            return d.courier
        return None

    async def cancel_delivery(self, id):
        d = await self.get_delivery(id)
        d.status = 'cancelled'

    async def accept_delivery(self, id, courier_id: str) -> None:
        d = await self.get_delivery(id)
        if d is not None:
            d.courier = courier_id
            d.status = 'in-process'

    async def finish_delivery(self, id: str) -> Delivery | None:
        d = await self.get_delivery(id)
        if d:
            d.status = 'delivered'
        return d

    async def add_delivery(self, delivery: Delivery):
        from courier.src.service import deliveries

        deliveries[delivery.id] = delivery
