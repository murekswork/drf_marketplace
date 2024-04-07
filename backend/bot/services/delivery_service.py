import datetime
import json
from typing import AsyncGenerator

from kafka_common.factories import async_send_kafka_msg
from kafka_common.receiver import SingletonMixin
from kafka_common.topics import DeliveryTopics
from repository.courier_repository import CourierRepository
from repository.delivery_repository import DeliveryRepository
from schemas.schemas import Courier, Delivery, cancelled_deliveries, Location
from utils import DistanceCalculator


class DeliveryService(SingletonMixin):
    __service_lock: bool = True
    __lock_counter: int = 0

    def __init__(self):
        self.delivery_repository = DeliveryRepository()
        self.courier_repository = CourierRepository()

    @property
    def lock(self):
        return self.__service_lock

    @lock.setter
    def lock(self, new_lock: bool) -> None:
        self.__service_lock = new_lock

    @property
    def lock_counter(self):
        return self.__lock_counter

    @lock_counter.setter
    def lock_counter(self, new_counter: int) -> None:
        self.__lock_counter = new_counter

    async def _verify_service(self):
        free_couriers = await self.courier_repository.get_by_kwargs(busy=False)
        if free_couriers:
            self.lock = False
            self.lock_counter = 0

    async def add_courier_to_line(self, courier: Courier):
        await self.courier_repository.add(courier)
        self.lock = False
        self.lock_counter = 0

    async def open_delivery(
            self, delivery: Delivery, k: int = 5, retries: int = 0
    ) -> dict[str, Courier | Delivery | bool] | dict[str, str | bool]:
        service = DistanceCalculator()
        couriers = await self.courier_repository.get_by_kwargs(busy=False)
        couriers_with_location = [
            courier for courier in couriers if courier.location is not None
        ]

        search_courier_result = await service.get_nearest_free_courier(
            delivery, couriers_with_location
        )

        if search_courier_result["success"]:
            courier: Courier = search_courier_result["courier"]
            await self.delivery_repository.update(
                id=delivery.id, courier=courier.id, status=3
            )
            await self.courier_repository.update(
                id=courier.id, current_delivery_id=delivery.id, busy=True
            )

            msg = json.dumps(delivery.__dict__, default=str)
            await async_send_kafka_msg(msg, DeliveryTopics.DELIVERED)

            return {"success": True, "courier": courier, "delivery": delivery}

        else:
            if retries < 5:
                return await self.open_delivery(delivery, k + 1, retries + 1)
            else:
                self.lock = True
                return {"success": False, "msg": "Too many retries to find courier!"}

    async def picked_up_delivery(self, courier_id: int) -> Delivery:
        delivery = await self.get_couriers_delivery(courier_id)
        if delivery:
            delivery.status = 4

        msg = json.dumps(delivery.__dict__, default=str)
        await async_send_kafka_msg(msg, DeliveryTopics.DELIVERED)

        return delivery

    async def get_couriers_delivery(self, courier_id: int) -> Delivery | None:
        courier = await self.courier_repository.get(courier_id)
        delivery = None
        if courier:
            d_id = courier.current_delivery_id
            delivery = await self.delivery_repository.get(d_id)
        return delivery

    async def close_delivery(self, delivery_id: int, status: int) -> None:
        delivery = await self.delivery_repository.get(delivery_id)
        courier = await self.courier_repository.get(delivery.courier)
        await self.delivery_repository.update(
            delivery_id, status=status, completed_at=datetime.datetime.now()
        )
        busy = status == 0
        await self.courier_repository.update(courier.id, busy=busy)

    async def check_service_lock(self) -> bool:
        if self.lock and self.lock_counter < 5:
            self.lock_counter += 1

        elif self.lock and self.lock_counter > 5:
            await self._verify_service()

        else:
            return False

        return True

    async def start_delivering(self) -> AsyncGenerator | None:
        lock_status = await self.check_service_lock()
        if lock_status is False:
            return self._distribute_deliveries()
        return None

    async def _distribute_deliveries(self) -> AsyncGenerator[Delivery, None]:
        undelivered_deliveries = await self.delivery_repository.get_by_kwargs(status=1)
        for delivery in undelivered_deliveries:
            if delivery is not None:
                res = await self.open_delivery(delivery)
                yield res
            else:
                yield None

    async def change_delivery_distance(self, distance: int) -> None:
        calculate_service = DistanceCalculator()
        calculate_service.working_range += distance


class DeliveryValidationService:
    __acceptable_distance_difference = 0.2  # kilometers

    def __init__(self, courier_id: int):
        self.distance_calculator = DistanceCalculator()
        self.delivery_repository = DeliveryRepository()
        self.courier_repository = CourierRepository()
        self.courier_id = courier_id

    async def validate_courier_on_point(self):
        courier = await self.courier_repository.get(self.courier_id)
        delivery = await self.delivery_repository.get(courier.current_delivery_id)
        if delivery.status == 3:
            point = Location(delivery.latitude, delivery.longitude)
        else:
            point = Location(delivery.consumer_latitude, delivery.consumer_longitude)
        distance = await self.distance_calculator.calculate_distance(courier.location, point)
        return distance <= self.__acceptable_distance_difference


class DeliveryCancellationService(SingletonMixin):

    def __init__(self):
        self.delivery_service = DeliveryService()
        self.cancelled_delivery_repository = DeliveryRepository(
            source=cancelled_deliveries
        )

    async def check_cancelled_deliveries(self) -> AsyncGenerator[Courier, None] | None:
        deliveries = await self.cancelled_delivery_repository.get_all()
        if deliveries:
            for delivery in deliveries:
                await self.delivery_service.delivery_repository.delete(delivery.id)
                await self.cancelled_delivery_repository.delete(delivery.id)
                courier = await self.delivery_service.courier_repository.update(
                    delivery.courier, busy=False, current_delivery_id=None
                )
                if courier:
                    yield courier
