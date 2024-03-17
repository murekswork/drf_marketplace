import json
import logging
from dataclasses import asdict

from kafka_common.sender import KafkaSender
from schemas import Delivery


class CourierLocationSender(KafkaSender):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def send(self, msg: str):
        # msg here shud be jsonified !!!
        try:
            self.send_message(msg, topic='courier_location')
        except Exception as e:
            logging.error(f'Could not send location from Tg to Django coz of {e}')


class CourierProfileAsker(KafkaSender):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def send(self, msg: str):
        # msg here shud be jsonified !!!
        try:
            self.send_message(msg, topic='ask_courier_profile')
        except Exception as e:
            logging.error(f'Could not send profile ask from Tg to Django coz of {e}')


class TgDeliverySender(KafkaSender):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def send(self, msg: str):
        # msg here shud be jsonified !!!
        try:
            self.send_message(msg, topic='delivered')
        except Exception as e:
            logging.error(f'Could not send delivery from Tg to Django coz of {e}')

    def send_delivery_to_django(self, delivery: Delivery):
        try:
            msg = {
                'delivery_id': delivery.id,
                'delivery': asdict(delivery)
            }
            self.send(msg=json.dumps(msg, default=str))
        except Exception as e:
            logging.error(f'Could not send delivery to tg coz of {e}')
