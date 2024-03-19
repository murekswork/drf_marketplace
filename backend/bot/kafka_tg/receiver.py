import json

from kafka_common.receiver import KafkaReceiver
from schemas import Courier, Delivery, couriers, deliveries


class CourierProfileReceiver(KafkaReceiver):
    _thread = None
    _topic = 'courier_profile'

    def post_consume_action(self, msg: str):
        msg_dict = json.loads(msg)
        c = msg_dict['courier']

        courier_dc = Courier(
            id=int(c['id']),
            username=c['username'],
            first_name=c['first_name'],
            last_name=c['last_name'],
            done_deliveries=c['done_deliveries'],
            balance=c['balance'],
            rank=c['rank']
        )
        couriers[courier_dc.id] = courier_dc


class TgDeliveryReceiver(KafkaReceiver):
    _thread = None
    _topic = 'to_deliver'

    def post_consume_action(self, msg: str):
        msg_dict = json.loads(msg)
        d = Delivery(**msg_dict['delivery'])
        deliveries[d.id] = d
