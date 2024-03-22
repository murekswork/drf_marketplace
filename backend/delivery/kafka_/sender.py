import json
import logging

from bot.kafka_common.receiver import SingletonMixin
from bot.kafka_common.sender import KafkaSender
from delivery.models import Delivery
from django.core.serializers import serialize


def send_delivery_to_tg(delivery_orm: Delivery):
    try:
        # delivery_dto = model_to_dataclass_converter(delivery_orm, DeliveryDTO)
        serialized_delivery = serialize('json', [delivery_orm])
        msg = {
            'delivery_id': delivery_orm.id,
            'delivery': serialized_delivery
        }
        sender = DjangoDeliverySender()
        sender.send(json.dumps(msg, default=str))
    except Exception as e:
        logging.error(f'Could not send delivery to tg coz of {e}')


class DjangoDeliverySender(KafkaSender, SingletonMixin):
    _topic = 'to_deliver'
