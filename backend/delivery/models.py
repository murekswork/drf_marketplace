from courier.models import Courier
from django.db import models
from order.models import Order


class Delivery(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='delivery')
    address = models.CharField(max_length=120)
    latitude = models.FloatField(blank=False, null=False)
    longitude = models.FloatField(blank=False, null=False)
    amount = models.FloatField(max_length=6)
    courier = models.ForeignKey(Courier, on_delete=models.SET_NULL, null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(max_length=10, blank=False, null=False, choices=(
        (1, 'In-process'),
        (2, 'Searching'),
        (3, 'Delivering'),
        (4, 'Delivered'),
        (0, 'Canceled')
    ), default='searching')

    def __str__(self):
        return f'{self.order_id} - {self.status}'

    def save(self, *args, **kwargs):
        from .kafka_.sender import send_delivery_to_tg
        super().save(*args, **kwargs)
        if self.status == 1:
            send_delivery_to_tg(self)

# @receiver(pre_save, sender=Order)
# def increase_product_sales_count(sender, instance, **kwargs):
#     try:
#         obj_before_save = sender.objects.get(pk=instance.pk)
#     except sender.DoesNotExist:
#         pass
#     else:
#         if obj_before_save.payment_status is False and instance.payment_status is True:
#             obj_before_save.product.sales_count += 1
#             obj_before_save.product.save()

# Create your models here.
