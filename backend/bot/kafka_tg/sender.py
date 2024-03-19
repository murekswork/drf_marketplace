import json
from dataclasses import asdict

from kafka_common.receiver import SingletonMixin
from kafka_common.sender import KafkaSender
from schemas import Delivery


class CourierLocationSender(KafkaSender, SingletonMixin):
    _topic = 'courier_location'


class CourierProfileAsker(KafkaSender, SingletonMixin):
    _topic = 'ask_courier_profile'


class TgDeliverySender(KafkaSender, SingletonMixin):
    _topic = 'delivered'

    def send_delivery_to_django(self, delivery: Delivery):
        try:
            msg = {
                'delivery_id': delivery.id,
                'delivery': asdict(delivery)
            }
            self.send(msg=json.dumps(msg, default=str))
        except Exception as e:
            self.logger.error(f'Could not send delivery to tg coz of {e}')
