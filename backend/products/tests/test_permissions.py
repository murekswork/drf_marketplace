from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from products.models import Product
from shop.models import Shop, ShopManager, ShopStaffGroup


class TestManagerPermissions(TestCase):

    def setUp(self):
        self.user_owner = get_user_model().objects.create_user(username='owner', email='ownermail@mail.com')
        self.product_manager = get_user_model().objects.create_user(username='product_manager',
                                                                    email='product_manager@mail.com')
        self.sales_manager = get_user_model().objects.create_user(username='sales_manager',
                                                                  email='sales_manager@mail.com')
        self.not_permitted_user = get_user_model().objects.create_user(username='test', email='test@mail.com')

        self.shop = Shop.objects.create(title='Shop', description='Shop description', user=self.user_owner)

        # Set product manager group and role
        self.product_manager_group = ShopStaffGroup.objects.create(group_name='product_managers')
        self.product_manager_group.permissions.set(Permission.objects.filter(codename__in=['create_shop_product',
                                                                                           'update_shop_product',
                                                                                           'delete_shop_product']))
        self.shop_product_manager_role = ShopManager(shop=self.shop, user=self.product_manager,
                                                     group=self.product_manager_group)
        self.product_manager_group.save()
        self.shop_product_manager_role.save()

        # Set sales manager group and role
        self.sales_manager_group = ShopStaffGroup.objects.create(group_name='sales_manager')
        self.sales_manager_group.permissions.set(Permission.objects.filter(codename__in=['create_shop_sale',
                                                                                         'update_shop_sale',
                                                                                         'delete_shop_sale']))
        self.shop_sales_manager = ShopManager(shop=self.shop, user=self.sales_manager, group=self.sales_manager_group)
        self.shop_sales_manager.save()

        self.product = Product.objects.create(shop=self.shop, title='product', content='content', price=12000,
                                              public=True)

        self.product_manager.refresh_from_db()

    def test_user_owner_access_permission_can_upload_product(self):
        self.client.force_login(self.user_owner)
        response = self.client.post(reverse('product-list'), data={'title': 'title',
                                                                   'content': 'content',
                                                                   'price': 12000,
                                                                   'quantity': 1,
                                                                   'shop': self.shop.id}, follow=True)
        self.assertTrue(response.status_code == 201)

    def test_user_owner_access_permission_can_update_product(self):
        self.client.force_login(self.user_owner)
        response = self.client.put(reverse('product-update', kwargs={'pk': self.product.pk}),
                                   data={'title': 'new title',
                                         'content': 'new content',
                                         'price': 25000}, content_type='application/json', follow=True)
        self.assertTrue(response.status_code == 200)

    def test_user_owner_access_permission_can_create_sale(self):
        ...

    def test_user_owner_access_permission_can_update_sale(self):
        ...

    def test_user_product_manager_access_permission_can_upload_product(self):
        self.client.force_login(self.product_manager)
        response = self.client.post(reverse('product-list'), data={'title': 'title2',
                                                                   'content': 'content2',
                                                                   'price': 12000,
                                                                   'quantity': 1,
                                                                   'shop': self.shop.id}, follow=True)
        self.assertTrue(response.status_code == 201)

    def test_user_product_manager_access_permission_can_update_product(self):
        self.client.force_login(self.product_manager)
        response = self.client.put(reverse('product-update', kwargs={'pk': self.product.pk}),
                                   data={'title': 'new title',
                                         'content': 'new content',
                                         'price': 25}, content_type='application/json')
        self.assertTrue(response.status_code == 200, 'updated product by product manager')

    def test_user_sales_manager_access_permission_can_not_upload_product(self):
        self.client.force_login(self.sales_manager)
        response = self.client.post(reverse('product-list'), data={'title': 'title3',
                                                                   'content': 'content3',
                                                                   'price': 12000,
                                                                   'quantity': 1,
                                                                   'shop': self.shop.id}, follow=True)
        self.assertTrue(response.status_code == 403)

    def test_user_sales_manager_access_can_not_delete_product(self):
        self.client.force_login(self.sales_manager)
        response = self.client.delete(reverse('product-delete', kwargs={'pk': self.product.pk}))
        self.assertTrue(response.status_code != 204)

    def test_user_sales_manager_access_permission_can_not_update_product(self):
        self.client.force_login(self.sales_manager)
        response = self.client.put(reverse('product-update', kwargs={'pk': self.product.pk}),
                                   data={'title': 'new title',
                                         'content': 'new content',
                                         'price': 25}, content_type='application/json', follow=True)
        self.assertTrue(response.status_code != 200)

    def test_user_product_manager_access_permission_can_delete_product(self):
        self.client.force_login(self.product_manager)
        response = self.client.delete(reverse('product-delete', kwargs={'pk': self.product.pk}))
        self.assertTrue(response.status_code == 204)

    def test_user_owner_access_permission_can_delete_product(self):
        new_pr = Product.objects.create(shop=self.shop, title='new title', content='new content', price=25555)
        self.client.force_login(self.user_owner)
        response = self.client.delete(reverse('product-delete', kwargs={'pk': new_pr.pk}))
        self.assertTrue(response.status_code == 204)
