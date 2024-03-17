import json
import logging
from dataclasses import asdict

from bot.kafka_common.sender import KafkaSender
from delivery.models import Delivery
from delivery.schemas import DeliveryDTO
from utils.adapters import model_to_dataclass_converter


def send_delivery_to_tg(delivery_orm: Delivery):
    try:
        delivery_dto = model_to_dataclass_converter(delivery_orm, DeliveryDTO)
        msg = {
            'delivery_id': delivery_orm.id,
            'delivery': asdict(delivery_dto)
        }
        sender = DjangoDeliverySender()
        sender.send(msg=json.dumps(msg, default=str))
    except Exception as e:
        logging.error(f'Could not send delivery to tg coz of {e}')


class DjangoDeliverySender(KafkaSender):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def send(self, msg: str):
        # msg here shud be jsonified !!!
        try:
            self.send_message(msg, topic='to_deliver')
        except Exception as e:
            logging.error(f'Could not send delivery info from Django to TG coz of {e}')
