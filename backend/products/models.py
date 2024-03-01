import datetime

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q

from category.models import Category


class Sale(models.Model):
    size = models.DecimalField(max_digits=4, decimal_places=2)
    end_date = models.DateTimeField(default=datetime.datetime.now() + datetime.timedelta(days=7))
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='sale')

    def __str__(self):
        return f'Sale for {self.product.title} {self.size}%'


class ProductQuerySet(models.QuerySet):

    def is_public(self):
        return self.filter(public=True)

    def search(self, query, user=None):
        lookup = Q(title__icontains=query) | Q(content__icontains=query)
        qs = self.is_public().filter(lookup)
        if user is not None:
            qs2 = self.filter(user=user).filter(lookup)
            qs = (qs | qs2).distinct()
        return qs


class ProductManager(models.Manager):

    def get_queryset(self, *args, **kwargs):
        return ProductQuerySet(self.model, using=self._db)

    def search(self, query, user=None):
        return self.get_queryset().search(query, user)


class Product(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, default=1)
    title = models.CharField(max_length=120)
    content = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=15, decimal_places=2, default=99.99)
    public = models.BooleanField(default=True)
    quantity = models.IntegerField(default=0)
    category = models.ManyToManyField(Category, null=True, blank=True, related_name='products')

    objects = ProductManager()

    @property
    def sale_price(self):
        return "%.2f" % (float(self.price) * 0.8)

    def get_discount(self):
        return 'Discount value'

    def __str__(self):
        return f'{self.title} for {self.price} from {self.user}'
# Create your models here.
