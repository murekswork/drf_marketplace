from courier.models import Courier
from django.core.serializers import serialize

from kafka_common.factories import producer_factory


def send_courier_profile_from_django_to_telegram(courier_dict: dict):
    courier_db = Courier.objects.filter(id=courier_dict["id"]).first()
    if courier_db is None:
        courier_db = Courier.objects.create(**courier_dict)
    serialized_courier = serialize("json", [courier_db])
    sender = producer_factory("courier_profile")
    sender.send(serialized_courier)
