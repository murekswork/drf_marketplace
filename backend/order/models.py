import datetime
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from products.models import Product


class OrderQuerySet(models.QuerySet):

    pass


class OrderManager(models.Manager):

    def user_orders(self, user):
        return self.get_queryset().filter(user=user)

    def get_not_reviewed_orders(self, user):
        qs = self.user_orders(user).filter(article=None)
        return qs

    def get_queryset(self, *args, **kwargs):
        return OrderQuerySet(self.model, using=self._db)


class Order(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(get_user_model(), blank=False, null=True, on_delete=models.SET_NULL)
    product = models.ForeignKey(Product, blank=False, null=True, related_name='orders', on_delete=models.SET_NULL)
    count = models.IntegerField(default=1, blank=True)
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
        return f'{self.id}, {self.amount}'
