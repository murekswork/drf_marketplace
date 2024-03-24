import datetime
import json
import math

from schemas.schemas import Courier, Delivery, Location


class DistanceCalculator:
    earth_radius = 6371
    working_range = 5
    avg_courier_speed = 10
    waiting_time = 0.1

    async def get_free_courier_and_estimated_delivery_time(
            self,
            pickup_point: Location,
            consumer_point: Location,
            free_couriers: dict[Courier, None],
            priority: int
    ) -> tuple[Courier, float] | None:
        """Method to search courier depending on his distance from passed point"""
        nearest_distance = float('inf')
        optimal_courier = None
        for courier in free_couriers:
            pickup_distance = await self.calculate_distance(courier.location, pickup_point)
            consumer_distance = await self.calculate_distance(courier.location, consumer_point)
            total_distance = pickup_distance + consumer_distance
            if (pickup_distance <= self.working_range + priority
                    and consumer_distance <= self.working_range + priority  # noqa
                    and total_distance < nearest_distance):  # noqa
                nearest_distance = total_distance
                optimal_courier = courier

            estimated_time = await self.get_estimated_delivery_time(nearest_distance)
            return optimal_courier, estimated_time
        return None

    async def get_estimated_delivery_time(self, distance: float) -> float:
        """Method to calculate estimated delivering time based on distance and avg couriers speed"""
        estimated_time_minutes = ((distance / self.avg_courier_speed) + self.waiting_time) * 60
        return estimated_time_minutes

    async def get_nearest_free_courier(
            self,
            delivery: Delivery,
            free_couriers: dict[Courier, None]
    ) -> dict[str, bool | Courier]:
        if free_couriers:
            courier_and_estimated_time = await self.get_free_courier_and_estimated_delivery_time(
                pickup_point=Location(delivery.latitude, delivery.longitude),
                consumer_point=Location(delivery.consumer_latitude, delivery.consumer_longitude),
                free_couriers=free_couriers,
                priority=delivery.priority
            )
            if courier_and_estimated_time:
                delivery.estimated_time = (
                    datetime.datetime.now() + datetime.timedelta(minutes=courier_and_estimated_time[1]))
                return {'success': True, 'courier': courier_and_estimated_time[0]}
            delivery.priority += 1
        return {'success': False, 'msg': 'There are no couriers available in current max-range radius'}

    async def calculate_distance(self, point1: Location, point2: Location) -> float:
        """Calculate distance between two points"""
        # Convert latitude and longitude from degrees to radians
        lat1, lon1 = math.radians(point1.lat), math.radians(point1.lon)
        lat2, lon2 = math.radians(point2.lat), math.radians(point2.lon)

        # Calculate differences
        dlat, dlon = lat2 - lat1, lon2 - lon1

        # Haversine formula
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        # Calculate distance
        distance = self.earth_radius * c

        return distance


def dict_to_dataclass(dict_: dict, dataclass_: type):
    """Function to convert dict to dataclass by same fields"""
    same_fields = {field: dict_[field] for field in dict_ if field in dataclass_.__annotations__}
    return dataclass_(**same_fields)


def consume_django_model_to_dataclass(serialized_model: str, dataclass_: type):
    """Function takes serialized django model and dataclass type and converts it to dataclass object"""
    deserialized_msg = json.loads(serialized_model)[0]
    model_dict = deserialized_msg['fields']
    model_dict['id'] = deserialized_msg.pop('pk')
    return dict_to_dataclass(model_dict, dataclass_)
