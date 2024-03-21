import json

from kafka_common.receiver import KafkaReceiver
from schemas.schemas import Courier, Delivery, couriers, deliveries


def dict_to_dataclass(d: dict, dataclass):
    """Function to convert dict to dataclass by same fields"""
    same_fields = {
        field: d[field] for field in d if field in dataclass.__annotations__
    }
    return dataclass(**same_fields)


class CourierProfileReceiver(KafkaReceiver):
    _thread = None
    _topic = 'courier_profile'

    def post_consume_action(self, msg: str):
        """Method deserializes incoming message to courier and adds courier profile to line"""
        deserialized_msg = json.loads(msg)[0]
        courier = deserialized_msg['fields']
        courier['id'] = deserialized_msg['pk']
        couriers[courier['id']] = dict_to_dataclass(courier, Courier)


class TgDeliveryReceiver(KafkaReceiver):
    _thread = None
    _topic = 'to_deliver'

    def post_consume_action(self, msg: str):
        """Method deserializes incoming message in delivery and adds delivery to queue"""
        msg_dict = json.loads(msg)
        d = json.loads(msg_dict['delivery'])[0]['fields']
        d['id'] = msg_dict['delivery_id']
        dataklass = dict_to_dataclass(d, Delivery)
        deliveries[d['id']] = dataklass
