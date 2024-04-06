import datetime
import logging

from repository.delivery_repository import DeliveryRepository
from schemas.schemas import Delivery


class AvgCourierSpeedProvider:

    def __init__(self):
        self.delivery_repository = DeliveryRepository()

    async def collect_completed_deliveries(self) -> list[Delivery]:
        deliveries = await self.delivery_repository.get_by_kwargs(status=5)
        return deliveries

    async def get_deliveries_distances_and_times(
        self, deliveries: list[Delivery]
    ) -> tuple[float, datetime.timedelta]:
        distances = 0
        times = datetime.timedelta(seconds=0)
        for delivery in deliveries:
            distances += delivery.distance
            times += delivery.completed_at - delivery.started_at
        logging.warning(f"CALCULATED DISTANCES AND TIMES ITS {distances}, {times}")
        return distances, times

    async def clear_deliveries_from_storage(self, deliveries: list[Delivery]):
        for delivery in deliveries:
            await self.delivery_repository.delete(delivery.id)

    async def get_avg_couriers_speed(self) -> float:
        try:
            completed_deliveries = await self.collect_completed_deliveries()
            if completed_deliveries:
                distances, times = await self.get_deliveries_distances_and_times(
                    completed_deliveries
                )
                avg_speed = distances / (times.total_seconds() / 3600)
                await self.clear_deliveries_from_storage(completed_deliveries)
                logging.error(
                    f"Successfuly calculated avg speed and speed is {avg_speed}"
                )
                return avg_speed
            logging.error("No new completed deliveries found")
        except Exception as e:
            logging.error(
                f"Some error in calculating avg courier speed {e}", exc_info=e
            )
