import logging

from courier import CourierServiceImpl
from delivery import DeliveryServiceImpl
from kafka_tg.sender import TgDeliverySender
from schemas import Courier, Delivery, Location


class DeliveryLogic:
    _instance = None
    __service_lock: bool = True
    __lock_counter: int = 0

    def __init__(self):
        self._delivery_service = DeliveryServiceImpl()
        self._courier_service = CourierServiceImpl()
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
        verification = await self._courier_service.get_free_couriers()
        if verification:
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

    async def close_delivery(self, delivery_id: int) -> None:

        delivery = await self._delivery_service.get_delivery(delivery_id)
        await self._delivery_service.finish_delivery(delivery_id)
        await self._courier_service.unlock_courier(delivery.courier)
        await self._courier_service.pay_courier(delivery.courier, delivery.amount)
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

# print(couriers)
# print(deliveries)
# print('\n\n\nBefore open deliveryw')
# print(service.open_delivery(d1))
# print(couriers)
# print(deliveries)
# print('\n\n\nAfter opened deliveryw')
# print(service.close_delivery(d1))
# print(couriers)
# print(deliveries)
# print('\n\n\nAfter closed deliveryw')
