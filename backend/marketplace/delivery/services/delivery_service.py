import logging

from delivery.adapters.delivery_adapters import DeliveryAdapter
from delivery.exceptions import DeliveryPickedUpException
from delivery.models import Delivery
from kafka_common.factories import producer_factory
from kafka_common.topics import DeliveryTopics


class DeliveryService:

    def cancel_by_customer(self, delivery: Delivery):
        if delivery.status > 3:
            # if delivery already picked up by courier
            raise DeliveryPickedUpException(
                "Can not cancel because delivery already picked up!"
            )
        delivery.status = 0
        delivery.save()
        sender = producer_factory(DeliveryTopics.TO_CANCEL_DELIVERY)
        msg = DeliveryAdapter.serialize_delivery(delivery)
        sender.send(msg)
