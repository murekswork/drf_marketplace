from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db import models
from django.utils.text import slugify


@dataclass
class ShopPermissions:
    CREATE_PRODUCT = Permission.objects.get(codename='create_shop_product')
    UPDATE_PRODUCT = Permission.objects.get(codename='update_shop_product')
    DELETE_PRODUCT = Permission.objects.get(codename='delete_shop_product')

    CREATE_SALE = Permission.objects.get(codename='create_shop_sales')
    UPDATE_SALE = Permission.objects.get(codename='update_shop_sales')
    DELETE_SALE = Permission.objects.get(codename='delete_shop_sales')

    MANAGE_SHOP_DATA = Permission.objects.get(codename='manage_shop_data')
    MANAGE_MANAGERS = Permission.objects.get(codename='manage_shop_managers')

    CREATE_PRODUCT_UPLOAD = Permission.objects.get(codename='create_product_upload')
    DELETE_PRODUCT_UPLOAD = Permission.objects.get(codename='delete_product_upload')
    READ_PRODUCT_UPLOAD = Permission.objects.get(codename='read_product_upload')


class ShopQuerySet(models.QuerySet):
    pass


class ShopObjectManager(models.Manager):

    def get_queryset(self):
        return ShopQuerySet(self.model, using=self._db)


class ShopStaffGroup(models.Model):
    group_name = models.CharField(max_length=120, default='Group name')
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        limit_choices_to={
            'codename__in': [
                'create_shop_product',
                'update_shop_product',
                'delete_shop_product',
                'create_shop_sales',
                'update_shop_sales',
                'delete_shop_sales',
                'manage_shop_data',
                'manage_shop_managers',
                'create_product_upload',
                'delete_product_upload',
                'read_product_upload',
            ],
        },
    )

    def has_permission(self, permission: str | Permission = None):
        if not isinstance(permission, Permission):
            permission_instance = Permission.objects.filter(codename=permission)
            if permission_instance.exists():
                return permission_instance[0] in self.permissions.prefetch_related()
        else:
            return permission in self.permissions.prefetch_related()

    def __str__(self):
        return f'{self.group_name}'


class ShopManager(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name='manager_roles',
    )
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=120, default='Shop manager title')
    group = models.ForeignKey('ShopStaffGroup', on_delete=models.SET_NULL, null=True)

    def has_permission(self, permission):
        if self.user == self.shop.user:
            return True

        if self.group:
            return self.group.has_permission(permission)
        return False

    def __str__(self):
        return f'{self.title} - {self.shop}'


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
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name='shops_owned',
    )
    title = models.CharField(max_length=120, default='Shop Title')
    description = models.TextField(max_length=500, default='Shop Description')
    active = models.BooleanField(default=True)
    managers = models.ManyToManyField(through=ShopManager, to=get_user_model())
    slug = models.SlugField(unique=True, max_length=500, editable=False)

    objects = ShopObjectManager()

    class Meta:
        permissions = [
            ('create_shop_product', 'Can create shop products'),
            ('update_shop_product', 'Can update shop products'),
            ('delete_shop_product', 'Can delete shop products'),
            ('upload_many_product', 'Can upload many products'),
            ('create_shop_sales', 'Can create shop sales'),
            ('update_shop_sales', 'Can update shop sales'),
            ('delete_shop_sales', 'Can delete shop sales'),
            ('manage_shop_data', 'Can manage shop data'),
            ('manage_shop_managers', 'Can grant shop permission to other users'),
            ('create_product_upload', 'Can create product uploads'),
            ('delete_product_upload', 'Can delete product uploads'),
            ('read_product_upload', 'Can read product uploads'),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Shop.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

        if not self.managers.select_related():
            owner = ShopManager(title='Shop Owner', user=self.user, shop=self)
            owner.save()

    def is_active(self):
        return self.active
