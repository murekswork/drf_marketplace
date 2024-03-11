import datetime
import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from products.models import Product


class OrderQuerySet(models.QuerySet):

    def paid_orders(self):
        qs = self.filter(payment_status=True).order_by('-created_at')
        return qs


class OrderManager(models.Manager):

    def user_orders(self, user):
        return self.get_queryset().filter(user=user)

    def get_not_reviewed_orders(self, user):
        paid_qs = self.user_paid_orders(user)
        qs = paid_qs.filter(article=None)
        return qs

    def get_queryset(self, *args, **kwargs):
        return OrderQuerySet(self.model, using=self._db)

    def user_paid_orders(self, user):
        user_qs = self.user_orders(user=user)
        paid_qs = user_qs.paid_orders()
        return paid_qs


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(get_user_model(), blank=False, null=True, on_delete=models.SET_NULL)
    product = models.ForeignKey(Product, blank=False, null=True, related_name='orders', on_delete=models.SET_NULL)
    count = models.IntegerField(default=1, blank=True, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, blank=False, null=True, default=0.00)
    payment_status = models.BooleanField(default=False, editable=True)
    lifetime = models.DateTimeField(default=datetime.datetime.now() + datetime.timedelta(minutes=2))
    # review = models.ForeignKey(Article, on_delete=models.SET_NULL, null=True, blank=True, default=None)

    objects = OrderManager()

    @property
    def total_amount(self):
        self.amount = self.product.price * self.count
        return self.amount

    def __str__(self):
        return f'Order #{self.id}'


@receiver(pre_save, sender=Order)
def increase_product_sales_count(sender, instance, **kwargs):
    try:
        obj_before_save = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        pass
    else:
        if obj_before_save.payment_status is False and instance.payment_status is True:
            obj_before_save.product.sales_count += 1
            obj_before_save.product.save()
