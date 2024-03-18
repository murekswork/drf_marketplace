import time

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run kafka message listeners'

    def handle(self, *args, **options):
        from courier.kafka_.receiver import (
            CourierProfileAskReceiver,
            ReceiveCourierLocation,
        )
        from delivery.kafka_.receiver import DjangoDeliveryReceiver
        location_receiver = ReceiveCourierLocation()
        location_receiver.start_listening()

        profile_ask_receiver = CourierProfileAskReceiver()
        profile_ask_receiver.start_listening()

        delivery_update_receiver = DjangoDeliveryReceiver()
        delivery_update_receiver.start_listening()

        time.sleep(1000000)
