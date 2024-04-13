import logging

from courier.models import Courier
from django.db import models
from django.utils import timezone
# from kafka_common.topics import DeliveryTopics
from order.models import Order


class Delivery(models.Model):
    order_id = models.ForeignKey(
        Order, on_delete=models.PROTECT, related_name='delivery'
    )
    address = models.CharField(max_length=120)
    latitude = models.FloatField(blank=False, null=False)
    consumer_latitude = models.FloatField(blank=False, null=False)
    longitude = models.FloatField(blank=False, null=False)
    consumer_longitude = models.FloatField(blank=False, null=False)
    amount = models.FloatField(max_length=6)
    courier = models.ForeignKey(
        Courier, on_delete=models.SET_NULL, null=True, blank=True
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(
        blank=False,
        null=False,
        choices=(
            (1, 'In-process'),
            (2, 'Searching'),
            (3, 'Delivering'),
            (4, 'Picked Up'),
            (5, 'Delivered'),
            (0, 'Canceled'),
        ),
        default=1,
    )

    def __str__(self):
        return f'{self.order_id} - {self.status}'

    # def save(self, *args, **kwargs):
    #     # TODO: REMOVE THIS FROM DATABASE LAYER
    #     super().save(*args, **kwargs)
    #     if self.status == 1:
    #         from delivery.adapters.delivery_adapters import DeliveryAdapter
    #         from kafka_common.factories import send_kafka_msg
    #
    #         msg = DeliveryAdapter.serialize_delivery(self)
    #         send_kafka_msg(msg, DeliveryTopics.TO_DELIVER)
    #         logging.warning('Sent delivery to telegram !')
    #
    #     elif self.status == 5:
    #         self.completed_at = timezone.now()
    #         super().save(*args, **kwargs)
