import json
from dataclasses import asdict

from kafka_tg.sender import CourierLocationSender, CourierProfileAsker, TgDeliverySender
from schemas.schemas import Delivery, Location, couriers
from telegram._chat import Chat
from telegram._message import Message


class CourierService:

    async def courier_start_carrying(self, user: Chat):
        courier = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        }

        kafka_ = CourierProfileAsker()
        kafka_.send(json.dumps(courier))

    async def courier_stop_carrying(self, user: Chat):
        courier = couriers.pop(user.id)
        return courier

    async def track_location(self, msg: Message, user: Chat):
        loc = Location(msg.location.latitude, msg.location.longitude)

        couriers[user.id].location = loc

        msg = {'courier_id': user.id, 'location': asdict(loc)}
        kafka_ = CourierLocationSender()
        kafka_.send(json.dumps(msg))

    async def close_delivery(self, cour_id: int, status: int) -> Delivery:
        from services.delivery_service import DeliveryService
        service = DeliveryService()
        delivery = await service.get_couriers_delivery(cour_id)
        delivery.status = status
        if delivery:
            await service.close_delivery(delivery.id, status)

            kafka_ = TgDeliverySender()
            kafka_.send_delivery_to_django(delivery)
        return delivery
