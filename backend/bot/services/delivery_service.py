import logging
import math

from kafka_common.receiver import SingletonMixin
from kafka_tg.sender import TgDeliverySender
from managers.courier import CourierManagerImpl
from managers.delivery import DeliveryManagerImpl
from schemas.schemas import Courier, Delivery, Location


class DeliveryService:
    _instance = None
    __service_lock: bool = True
    __lock_counter: int = 0

    def __init__(self):
        self._delivery_service = DeliveryManagerImpl()
        self._courier_service = CourierManagerImpl()
        self._kafka_delivery_service: TgDeliverySender = TgDeliverySender()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def __lock_service(self):
        self.__service_lock = True

    async def __unlock_service(self):
        self.__service_lock = False

    async def __verify_service(self):
        free_couriers = await self._courier_service.get_free_couriers()
        if free_couriers:
            self.__service_lock = False

        self.__lock_counter = 0

    async def add_courier(self, courier: Courier):
        await self._courier_service.add_courier(courier)
        await self.__unlock_service()

    async def open_delivery(
            self,
            delivery: Delivery,
            k: int = 5,
            retries: int = 0
    ) -> dict[str, Courier | Delivery | bool] | dict[str, str | bool]:

        # TODO : CONSIDER HOW TO GET POINT, OR MAYBE CHANGE FUNCTION AND MAKE IT TAKE (PURE LATIT AND LONGIT)
        del_point = Location(delivery.latitude, delivery.longitude)
        search_cour_res = await self._courier_service.get_nearest_free_courier(del_point, k)

        if search_cour_res['success'] is True:
            c: Courier = search_cour_res['courier']
            await self._delivery_service.accept_delivery(id=delivery.id, courier_id=c.id)
            await self._courier_service.set_delivery(c.id, delivery.id)

            self._kafka_delivery_service.send_delivery_to_django(delivery=delivery)

            return {'success': True, 'courier': c, 'delivery': delivery}

        else:
            if retries < 5:
                return await self.open_delivery(delivery, k + 1, retries + 1)
            else:
                await self.__lock_service()
                return {'success': False, 'msg': 'Too many retries to find courier!'}
        # return {'success': False, 'msg': 'No courier found'}

    async def get_couriers_delivery(self, courier_id: int) -> Delivery | None:
        c = await self._courier_service.get_courier(courier_id)
        d = None
        if c:
            d_id = c.current_delivery_id
            d = await self._delivery_service.get_delivery(d_id)
        return d

    async def close_delivery(self, delivery_id: int, status: int) -> None:
        closing_service = DeliveryClosingService()
        await closing_service.close_delivery(delivery_id, status=status)
        await self.__unlock_service()

    async def start_delivering(self):
        # Firstly check if service is locked then ++ counterer and return if it is and lock_counterer < 5
        if self.__service_lock is True and self.__lock_counter < 5:
            logging.warning('Service is locked now because no free couriers!')
            self.__lock_counter += 1
            return

        # Check if service is locked then if lock counterer > 5 then verify couriers busy status and unlock if
        # any couriers is free
        elif self.__service_lock is True and self.__lock_counter > 5:
            await self.__verify_service()
            return

        undelivered = await self._delivery_service.get_undelivered_deliveries()
        for u in undelivered:
            if u is not None:
                res = await self.open_delivery(u)
                yield res
            else:
                yield None

    async def change_delivery_distance(self, distance: int) -> None:
        calculate_service = DistanceCalculator()
        calculate_service.working_range += distance


class DeliveryClosingService:

    def __init__(self):
        self.courier_service = CourierManagerImpl()
        self.delivery_service = DeliveryManagerImpl()

    async def close_success_delivery(self, delivery: Delivery):
        await self.delivery_service.finish_delivery(delivery.id, status=4)
        await self.courier_service.unlock_courier(delivery.courier)

    async def close_not_success_delivery(self, delivery: Delivery):
        await self.delivery_service.finish_delivery(delivery.id, status=0)

    async def close_delivery(self, delivery_id: int, status: int):
        d: Delivery = await self.delivery_service.get_delivery(delivery_id)
        if status == 4:
            await self.close_success_delivery(d)
        else:
            await self.close_not_success_delivery(d)


class DistanceCalculator(SingletonMixin):
    earth_radius = 6371
    working_range = 5

    async def search_courier_by_distance(self, point: Location, couriers) -> Courier | None:
        """Method to search courier depending on his distance from passed point"""
        nearest_distance = float('inf')
        cour = None
        for c in couriers:
            c_distance = await self._haversine(lat1=c.location.lat, lon1=c.location.lon, lat2=point.lat, lon2=point.lon)
            if c_distance <= self.working_range and c_distance <= nearest_distance:
                nearest_distance = c_distance
                cour = c
        return cour

    async def _haversine(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points"""
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
