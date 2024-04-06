import datetime
import logging

from geopy import distance

from schemas.schemas import Courier, Delivery, Location


class DistanceCalculator:
    earth_radius = 6371
    working_range = 5
    avg_courier_speed: float = 10  # should be in km/h
    waiting_time = 0.05  # should be in hours

    @classmethod
    async def set_avg_courier_speed(cls, new_speed: float) -> None:
        logging.error(f"Setting avg courier sped to {new_speed}")
        cls.avg_courier_speed = new_speed

    async def get_courier_etime_distance(
        self,
        pickup_point: Location,
        consumer_point: Location,
        free_couriers: list[Courier],
        priority: int,
    ) -> tuple[Courier, float, float] | tuple[None, None, None]:
        """Method to search courier depending on his distance from passed point"""
        nearest_distance = float("inf")
        optimal_courier = None
        for courier in free_couriers:
            courier_distance = await self.calculate_distance(
                courier.location, pickup_point, consumer_point
            )
            if courier_distance <= self.working_range * 2:  # noqa
                nearest_distance = courier_distance
                optimal_courier = courier

            estimated_time = await self.get_estimated_delivery_time(nearest_distance)
            return optimal_courier, estimated_time, nearest_distance
        return None, None, None

    async def get_estimated_delivery_time(self, distance: float) -> float:
        """Method to calculate estimated delivering time based on distance and avg couriers speed"""
        estimated_time_minutes = (
            (distance / self.avg_courier_speed) + self.waiting_time
        ) * 60
        return estimated_time_minutes

    async def get_nearest_free_courier(
        self, delivery: Delivery, free_couriers: list[Courier] | None
    ) -> dict[str, bool | Courier]:
        if free_couriers:
            courier, estimated_time, distance = await self.get_courier_etime_distance(
                pickup_point=Location(delivery.latitude, delivery.longitude),
                consumer_point=Location(
                    delivery.consumer_latitude, delivery.consumer_longitude
                ),
                free_couriers=free_couriers,
                priority=delivery.priority,
            )
            if courier:
                delivery.estimated_time = datetime.datetime.now() + datetime.timedelta(
                    minutes=estimated_time
                )  # type: ignore
                delivery.distance = distance
                return {"success": True, "courier": courier}
            delivery.priority += 1
        return {
            "success": False,
            "msg": "There are no couriers available in current max-range radius",
        }

    async def calculate_distance(self, *points: Location) -> float:
        total_distance = 0
        for i in range(1, len(points)):
            total_distance += distance.distance(
                (points[i - 1].lat, points[i - 1].lon), (points[i].lat, points[i].lon)
            ).kilometers
        return total_distance
