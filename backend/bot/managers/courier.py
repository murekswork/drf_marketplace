from abc import ABC, abstractmethod

from schemas.schemas import Courier, Location
from services.delivery_service import DistanceCalculator


class CourierManagerAbc(ABC):

    @abstractmethod
    async def get_courier(self, id: int) -> Courier:
        raise NotImplementedError

    @abstractmethod
    async def get_all_couriers(self) -> list[Courier]:
        raise NotImplementedError

    @abstractmethod
    async def get_free_couriers(self) -> list[Courier]:
        raise NotImplementedError

    @abstractmethod
    async def get_nearest_free_courier(self, point: Location, k: int = 5) -> Courier | None:
        raise NotImplementedError

    @abstractmethod
    async def lock_courier(self, id: int):
        raise NotImplementedError

    @abstractmethod
    async def unlock_courier(self, id: int):
        raise NotImplementedError

    @abstractmethod
    async def add_courier(self, courier: Courier):
        raise NotImplementedError


class CourierManagerImpl(CourierManagerAbc):

    async def get_courier(self, id: int) -> Courier | None:
        from schemas.schemas import couriers
        c = couriers.get(id, None)
        return c

    async def get_all_couriers(self) -> list[Courier]:
        from schemas.schemas import couriers
        return list(couriers.values())

    async def get_free_couriers(self) -> list[Courier | None]:
        from schemas.schemas import couriers
        cs = [c for c in couriers.values() if c.busy is False and c.location is not None]
        return cs

    async def get_nearest_free_courier(self, point: Location, k: int = 5) -> dict[str, bool | Courier]:
        free_couriers = await self.get_free_couriers()

        if not free_couriers:
            return {'success': False, 'msg': 'No free couriers available now '}

        service = DistanceCalculator()
        courier = await service.search_courier_by_distance(point=point, couriers=free_couriers)
        if courier:
            return {'success': True, 'courier': courier}

        return {'success': False, 'msg': 'There are no couriers available in current max-range radius'}

    async def lock_courier(self, id: int) -> None:
        c = await self.get_courier(id)
        if c:
            c.busy = True

    async def set_delivery(self, courier_id: int, delivery_id: int) -> None:
        await self.lock_courier(courier_id)
        c = await self.get_courier(courier_id)
        if c:
            c.current_delivery_id = delivery_id

    async def unlock_courier(self, id: int):
        c = await self.get_courier(id)
        if c:
            c.busy = False
            c.current_delivery_id = None

    async def add_courier(self, courier: Courier) -> None:
        from schemas.schemas import couriers
        couriers[courier.id] = courier
