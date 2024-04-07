import json
from dataclasses import asdict

from kafka_common.factories import async_send_kafka_msg
from kafka_common.topics import CourierTopics, DeliveryTopics
from schemas.schemas import Delivery, Location, couriers
from telegram._chat import Chat
from telegram._message import Message


class CourierService:

    async def courier_start_carrying(self, user: Chat):
        courier = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }

        msg = json.dumps(courier)
        await async_send_kafka_msg(msg, CourierTopics.COURIER_PROFILE_ASK)

    async def courier_stop_carrying(self, user: Chat):
        courier = couriers.pop(user.id)
        return courier

    async def track_location(self, msg: Message, user: Chat):
        loc = Location(msg.location.latitude, msg.location.longitude)

        couriers[user.id].location = loc

        msg = {"courier_id": user.id, "location": asdict(loc)}
        await async_send_kafka_msg(json.dumps(msg), CourierTopics.COURIER_LOCATION)

    async def close_delivery(self, cour_id: int, status: int) -> Delivery:
        from services.delivery_service import DeliveryService

        service = DeliveryService()
        delivery = await service.get_couriers_delivery(cour_id)
        delivery.status = status
        if delivery:
            await service.close_delivery(delivery.id, status)

            msg = json.dumps(delivery.__dict__, default=str)
            await async_send_kafka_msg(msg, DeliveryTopics.DELIVERED)

        return delivery
