from kafka_common.receiver import KafkaReceiver
from schemas.schemas import Courier, Delivery, couriers, deliveries
from utils import consume_django_model_to_dataclass


class CourierProfileReceiver(KafkaReceiver):
    _topic = 'courier_profile'

    def post_consume_action(self, msg: str) -> None:
        """Method to deserialize incoming message from to courier and adds courier profile to line"""
        courier_dataclass = consume_django_model_to_dataclass(msg, Courier)
        courier_dict = courier_dataclass.__dict__

        if courier_dict['id'] not in couriers:
            couriers[courier_dict['id']] = courier_dataclass
        else:
            for field in courier_dict:
                if courier_dict.get(field, None):
                    couriers[courier_dict['id']].__dict__[field] = courier_dict[field]


class TgDeliveryReceiver(KafkaReceiver):
    _topic = 'to_deliver'

    def post_consume_action(self, msg: str) -> None:
        """Method to deserialize incoming message in delivery and adds delivery to queue"""
        delivery_dataclass = consume_django_model_to_dataclass(msg, Delivery)
        deliveries[delivery_dataclass.id] = delivery_dataclass
