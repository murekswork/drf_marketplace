import json

from bot.kafka_common.receiver import KafkaReceiver
from courier.kafka_.sender import send_courier_profile_from_django_to_telegram
from courier.services import CourierDeliveryService
from delivery.services.delivery_service import DeliveryUtils


class DjangoDeliveryReceiver(KafkaReceiver):
    _thread = None
    _topic = 'delivered'

    def post_consume_action(self, msg: str):
        msg_dict: dict = json.loads(msg)
        delivery_dict = msg_dict['delivery']

        d_service = DeliveryUtils()
        delivery_db = d_service.update_delivery_in_db_from_telegrma(delivery_dict)

        c_service = CourierDeliveryService()
        courier_db = c_service.close_delivery(delivery_db)
        if delivery_db.status == 5:
            send_courier_profile_from_django_to_telegram({'id': courier_db.id})
