from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db import models

from products.models import Product
from articles.models import Article


class ShopQuerySet(models.QuerySet):
    ...


class ShopObjectManager(models.Manager):

    def get_queryset(self):
        return ShopQuerySet(self.model, using=self._db)


class ShopStaffGroup(models.Model):
    group_name = models.CharField(max_length=120, default='Group name')
    permissions = models.ManyToManyField(Permission, blank=True, limit_choices_to={
        'codename__in': ['add_product', 'delete_product', 'delete_sale', 'change_product', 'change_sale', 'add_sale'],
        })

    def __str__(self):
        return f'{self.group_name}'


class ShopManager(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=120, null='Role title')
    group = models.ForeignKey('ShopStaffGroup', on_delete=models.SET_NULL, null=True)
    # permission = models.ForeignKey(Permission


class ProductUpload(models.Model):

    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    products_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    file_name = models.CharField(blank=True, max_length=250, null=True)

    def __str__(self):
        return f'Products upload from {self.user} at {self.created_at}'


class Shop(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, related_name='shop_owned')
    title = models.CharField(max_length=120, default='Shop Title')
    description = models.TextField(max_length=500, default='Shop Description')
    active = models.BooleanField(default=True)
    managers = models.ManyToManyField(through=ShopManager, to=get_user_model())

    objects = ShopObjectManager()

    def is_active(self):
        return self.active
