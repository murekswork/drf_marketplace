import datetime

from kafka_common.receiver import SingletonMixin
from repository.courier_repository import CourierRepository
from repository.delivery_repository import DeliveryRepository
from schemas.schemas import Delivery, Location
from utils import DistanceCalculator


class NotificationService(SingletonMixin):
    __notification_delta: int = 69  # must be in seconds!

    def __init__(self):
        self.delivery_repository = DeliveryRepository()
        self.courier_repository = CourierRepository()

    @property
    def notification_delta(self):
        return self.__notification_delta

    @notification_delta.setter
    def notification_delta(self, value: int):
        self.__notification_delta = value

    async def distribute_notifications(self) -> tuple[list[Delivery], list[Delivery]]:
        not_picked_up_deliveries = await self.delivery_repository.get_by_kwargs(
            status=3
        )
        picked_up_deliveries = await self.delivery_repository.get_by_kwargs(status=4)

        to_notify_set = list()
        time_out_set = list()
        for delivery in not_picked_up_deliveries + picked_up_deliveries:

            if delivery.estimated_time <= datetime.datetime.now():
                time_out_set.append(delivery)
                continue

            in_time = await self.check_delivery_timing(delivery)

            if not in_time:
                if not delivery.last_notification_ts or await self.check_last_notification_ts(delivery):
                    delivery.last_notification_ts = datetime.datetime.now()
                    to_notify_set.append(delivery)

        return to_notify_set, time_out_set

    async def check_delivery_timing(self, delivery: Delivery):
        courier = await self.courier_repository.get(delivery.courier)
        points = []
        if delivery.status == 3:
            points.append(Location(delivery.latitude, delivery.longitude))

        points.append(Location(delivery.consumer_latitude, delivery.consumer_longitude))

        calculator = DistanceCalculator()

        left_distance = await calculator.calculate_distance(courier.location, *points)
        left_distance_requiring_time = left_distance / calculator.avg_courier_speed

        in_time = await self.compare_actual_time_and_estimated_time(
            left_distance_requiring_time, delivery.estimated_time
        )
        return in_time

    async def check_last_notification_ts(self, delivery: Delivery) -> bool:
        # return True if from last notification timestamp left more than 2 minutes
        much_time_left = datetime.datetime.now() - delivery.last_notification_ts >= datetime.timedelta(
            seconds=self.notification_delta)
        return much_time_left

    async def compare_actual_time_and_estimated_time(
            self, left_time: float, estimated_time: datetime.datetime
    ) -> bool:
        # TODO: ITS DEBUG SETTING, REMOVE + TIMEDELTA IN PROD
        result = datetime.timedelta(hours=left_time) + datetime.datetime.now() <= estimated_time
        return result
