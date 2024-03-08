from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db import models
from django.utils.text import slugify


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
    slug = models.SlugField(unique=True, max_length=500, editable=False)

    objects = ShopObjectManager()

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Shop.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super(Shop, self).save(*args, **kwargs)

    def is_active(self):
        return self.active
