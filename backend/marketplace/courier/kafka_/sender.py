from functools import singledispatch

from courier.models import Courier
from django.core.serializers import serialize
from kafka_common.factories import send_kafka_msg
from kafka_common.topics import CourierTopics


@singledispatch
def send_courier_profile_from_django_to_telegram(courier_dict: dict):
    courier_db = Courier.objects.filter(id=int(courier_dict['id'])).first()
    if courier_db is None:
        courier_db = Courier.objects.create(**courier_dict)
    serialized_courier = serialize('json', [courier_db])
    send_kafka_msg(serialized_courier, CourierTopics.COURIER_PROFILE)
