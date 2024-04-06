from courier.models import Courier
from django.core.serializers import serialize
from kafka_common.receiver import SingletonMixin
from kafka_common.sender import KafkaSender


def send_courier_profile_from_django_to_telegram(courier_dict: dict):
    courier_db = Courier.objects.filter(id=courier_dict['id']).first()
    if not courier_db:
        courier_db = Courier.objects.create(**courier_dict)
    serialized_courier = serialize('json', [courier_db])
    producer = CourierProfileProducer()
    producer.send(msg=serialized_courier)


class CourierProfileProducer(KafkaSender, SingletonMixin):
    _topic = 'courier_profile'
