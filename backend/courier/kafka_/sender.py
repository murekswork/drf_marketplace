import logging

from bot.kafka_common.receiver import SingletonMixin
from bot.kafka_common.sender import KafkaSender
from courier.models import Courier
from django.core.serializers import serialize


def send_courier_profile_from_django_to_telegram(courier_dict: dict):
    try:
        c = Courier.objects.filter(id=courier_dict['id']).first()
        if c is None:
            if not courier_dict['username']:
                courier_dict['username'] = courier_dict['first_name'] + courier_dict['last_name']
            c = Courier.objects.create(**courier_dict)

        serialized_c = serialize('json', [c])

        producer = CourierProfileProducer()
        producer.send(msg=serialized_c)

    except Exception as e:
        logging.error(f'Could not send courier profile from Django to Tg, coz of {e}')


class CourierProfileProducer(KafkaSender, SingletonMixin):
    _topic = 'courier_profile'
