import json
from dataclasses import dataclass

from kafka_common.receiver import KafkaReceiver
from schemas.schemas import Courier, Delivery, couriers, deliveries


def dict_to_dataclass(dict_: dict, dataclass_: type):
    """Function to convert dict to dataclass by same fields"""
    same_fields = {
        field: dict_[field] for field in dict_ if field in dataclass_.__annotations__
    }
    return dataclass(**same_fields)


def consume_django_model_to_dataclass(serialized_model: str, dataclass_: type):
    """Function takes serialized django model and dataclass type and converts it to dataclass object"""
    deserialized_msg = json.loads(serialized_model)[0]
    model_dict = deserialized_msg['fields']
    model_dict['id'] = deserialized_msg.pop('pk')
    courier_dataclass = dict_to_dataclass(model_dict, dataclass_)
    return courier_dataclass


class CourierProfileReceiver(KafkaReceiver):
    _topic = 'courier_profile'

    def post_consume_action(self, msg: str) -> None:
        """Method deserializes incoming message to courier and adds courier profile to line"""
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
        """Method deserializes incoming message in delivery and adds delivery to queue"""
        delivery_dataclass = consume_django_model_to_dataclass(msg, Delivery)
        deliveries[delivery_dataclass.id] = delivery_dataclass
