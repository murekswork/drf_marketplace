import json

from courier.kafka_.sender import send_courier_profile_from_django_to_telegram
from courier.services import CourierDeliveryService
from delivery.adapters.delivery_adapters import DeliveryAdapter
from kafka_common.receiver import KafkaReceiver
from kafka_common.topics import DeliveryTopics


class DjangoDeliveryReceiver(KafkaReceiver):
    _topic = DeliveryTopics.DELIVERED

    def post_consume_action(self, msg: str):
        delivery_dict: dict = json.loads(msg)

        adapter = DeliveryAdapter()
        delivery_db = adapter.update_delivery_in_db_from_telegrma(delivery_dict)

        c_service = CourierDeliveryService()
        courier_db = c_service.close_delivery(delivery_db)
        if delivery_db.status == 5:
            send_courier_profile_from_django_to_telegram({"id": courier_db.id})
