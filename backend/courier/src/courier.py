import math
from abc import ABC, abstractmethod

from courier.schemas import Courier, Location


class CourierService(ABC):

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


class CourierServiceImpl(CourierService):
    MAX_WORKING_RANGE = 10000
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def get_courier(self, id: int) -> Courier | None:
        from courier.src.service import couriers
        c = couriers.get(id, None)
        return c

    async def get_all_couriers(self) -> list[Courier]:
        from courier.src.service import couriers
        return list(couriers.values())

    async def get_free_couriers(self) -> list[Courier | None]:
        from courier.src.service import couriers
        cs = [c for c in couriers.values() if c.busy is False and c.location is not None]
        return cs

    async def get_nearest_free_courier(self, point: Location, k: int = 5) -> dict[str, bool | Courier]:
        free_couriers = await self.get_free_couriers()

        if not free_couriers:
            return {'success': False, 'msg': 'No free couriers available now '}

        service = DistanceCalculator()
        cour = await service.search_courier_by_distance(point=point, couriers=free_couriers)
        if cour:
            return {'success': True, 'courier': cour}

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

    async def pay_courier(self, courier_id: int, amount: float) -> None:
        c = await self.get_courier(courier_id)
        if c:
            c.balance += amount
            c.done_deliveries += 1

    async def add_courier(self, courier: Courier) -> None:
        from courier.src.service import couriers
        couriers[courier.id] = courier


class DistanceCalculator:
    _instance = None
    earth_radius = 6371
    working_range = 5

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def search_courier_by_distance(self, point: Location, couriers) -> Courier | None:
        nearest_distance = float('inf')
        cour = None
        for c in couriers:
            c_distance = await self.haversine(lat1=c.location.lat, lon1=c.location.lon, lat2=point.lat, lon2=point.lon)
            if c_distance <= self.working_range and c_distance <= nearest_distance:
                nearest_distance = c_distance
                cour = c
        return cour
        # if cour:
        #     return {'success': True, 'courier': cour}
        # else

    async def haversine(self, lat1, lon1, lat2, lon2):
        # Convert latitude and longitude from degrees to radians
        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)

        # Calculate differences
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Haversine formula
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        # Calculate distance
        distance = self.earth_radius * c

        return distance
