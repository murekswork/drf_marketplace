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
        logging.warning("STARTED TO SENT DEL")
        delivery.status = 0
        delivery.save()
        topic = DeliveryTopics.TO_CANCEL_DELIVERY
        sender = producer_factory(topic)
        msg = DeliveryAdapter.serialize_delivery(delivery)
        logging.warning("STARTED TO SENT DEL MESS IS {}".format(msg))
        sender.send(msg)
        logging.warning("SENT MSG {}".format(msg))
