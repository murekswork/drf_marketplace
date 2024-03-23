import datetime
import math

from schemas.schemas import Courier, Delivery, Location


class DistanceCalculator:
    earth_radius = 6371
    working_range = 5
    avg_courier_speed = 10
    waiting_time = 0.1

    async def search_courier_by_distance(
            self,
            pickup_point: Location,
            consumer_point: Location,
            couriers: dict[Courier, None],
            priority: int
    ) -> tuple[Courier, float] | None:
        """Method to search courier depending on his distance from passed point"""
        nearest_distance = float('inf')
        optimal_courier = None
        for c in couriers:
            pickup_distance = await self._haversine(
                lat1=c.location.lat, lon1=c.location.lon,
                lat2=pickup_point.lat, lon2=pickup_point.lon
            )
            consumer_distance = await self._haversine(
                lat1=c.location.lat, lon1=c.location.lon,
                lat2=consumer_point.lat, lon2=consumer_point.lon
            )
            total_distance = pickup_distance + consumer_distance
            if all((pickup_distance <= self.working_range + priority,
                   consumer_distance <= self.working_range + priority,
                   total_distance < nearest_distance)):

                nearest_distance = total_distance
                optimal_courier = c

        if not optimal_courier:
            return None

        estimated_time_minutes = ((nearest_distance / self.avg_courier_speed) + self.waiting_time) * 60
        return optimal_courier, estimated_time_minutes

    async def get_nearest_free_courier(self, delivery: Delivery, free_couriers: dict[Courier, None]) -> dict[str, bool | Courier]:

        if not free_couriers:
            return {'success': False, 'msg': 'No free couriers available now '}

        service = DistanceCalculator()
        courier = await service.search_courier_by_distance(
            pickup_point=Location(lat=delivery.latitude, lon=delivery.longitude),
            consumer_point=Location(lat=delivery.consumer_latitude, lon=delivery.consumer_longitude),
            couriers=free_couriers,
            priority=delivery.priority
        )
        if courier:
            delivery.estimated_time = datetime.datetime.now() + datetime.timedelta(minutes=courier[1])
            return {'success': True, 'courier': courier[0]}
        delivery.priority += 1
        return {'success': False, 'msg': 'There are no couriers available in current max-range radius'}

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
