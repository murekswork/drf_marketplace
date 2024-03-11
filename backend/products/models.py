import datetime

from category.models import Category
from django.db import models
from django.db.models import Avg, Count, Q
from shop.models import Shop


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

    def fetch_related(self, *args, **kwargs):
        qs = (self.get_queryset().prefetch_related('articles', 'sales', 'orders').select_related().
              annotate(mark=Avg('articles__mark'),
                       sales_count=Count('orders', filter=Q(orders__payment_status=True))))
        return qs

    def search(self, query, shop=None):
        return self.get_queryset().search(query, shop)

    # def get_similar(self, ):


class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=120)
    content = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=15, decimal_places=2, default=99.99)
    public = models.BooleanField(default=False)
    quantity = models.IntegerField(default=0)
    category = models.ManyToManyField(Category, null=True, blank=True, related_name='products')

    mark = models.DecimalField(max_digits=4, decimal_places=2, default=5)
    sales_count = models.IntegerField(default=0)

    objects = ProductManager()

    def __str__(self):
        return f'{self.title} for {self.price}'


class Sale(models.Model):
    size = models.DecimalField(max_digits=4, decimal_places=2)
    end_date = models.DateTimeField(default=datetime.datetime.now() + datetime.timedelta(days=7))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales')

    def __str__(self):
        return f'{self.size} till {self.end_date}'
