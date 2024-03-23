import logging

from bot.kafka_common.receiver import SingletonMixin
from bot.kafka_common.sender import KafkaSender
from courier.models import Courier
from django.core.serializers import serialize


def send_courier_profile_from_django_to_telegram(courier_dict: dict):
    try:
        courier_db = Courier.objects.filter(id=courier_dict['id']).first()
        if courier_db is None:
            courier_db = Courier.objects.create(**courier_dict)
        serialized_courier = serialize('json', [courier_db])
        producer = CourierProfileProducer()
        producer.send(msg=serialized_courier)

    except Exception as e:
        logging.error(f'Could not send courier profile from Django to Tg, coz of {e}')


class CourierProfileProducer(KafkaSender, SingletonMixin):
    _topic = 'courier_profile'
