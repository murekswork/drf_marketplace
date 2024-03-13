from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from order.models import Order
from products.models import Product
from rest_framework import status
from shop.models import Shop
from wallet.models import Wallet

User = get_user_model()


class OrderListCreateAPIViewTestCase(TestCase):

    def setUp(self):
        self.user_seller = User.objects.create_user(
            username='test', email='test@email.com'
        )
        self.shop = Shop.objects.create(
            user=self.user_seller, title='shop', description='shop'
        )
        self.product = Product.objects.create(
            title='product1', content='content1', price=15, quantity=15, shop=self.shop
        )
        self.user = User.objects.create_user(
            username='user', email='uesr@email.com'
        )

    def test_order_list_create_return_empty_when_no_order(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('order-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['results'], [], 'Response not contains orders')

    def test_order_create_invalid_data_count(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('order-list'), data={'product': self.product.id,
                                                                 'count': 'asd'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'Invalid count provided')

    def test_order_create_invalid_data_product(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('order-list'), data={'product': 'hello',
                                                                 'count': 1})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'Invalid product catched')

    def test_order_create_no_data_product(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('order-list'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'No data provided')

    def test_order_list_create_valid_data(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('order-list'), data={'product': self.product.id,
                                                                 'count': 1})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'Valid data provided')

    def test_order_list_create_return_empty_when_have_orders(self):
        Order.objects.create(user=self.user, product=self.product)
        self.client.force_login(self.user)
        response = self.client.get(reverse('order-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.json()['results'], [], 'Response contains some orders')


class OrderPayAPIViewTestCase(TestCase):

    def setUp(self):
        self.user_seller = User.objects.create_user(
            username='test', email='test@email.com'
        )
        self.shop = Shop.objects.create(
            user=self.user_seller, title='shop', description='shop'
        )
        self.product = Product.objects.create(
            title='product1', content='content1', price=15, quantity=15, shop=self.shop
        )
        self.user = User.objects.create_user(
            username='user', email='uesr@email.com'
        )
        self.order = Order.objects.create(product=self.product, user=self.user, count=1)
        self.others_order = Order.objects.create(product=self.product, user=self.user_seller, count=1)

    def test_order_pay_when_invalid_order_passed(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('order-payment', kwargs={'pk': '2c565d7d-a971-451b-86f1-ec517d5a31ea'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_pay_when_other_user_order_passed(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('order-payment', kwargs={'pk': self.others_order.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_pay_when_user_has_no_wallet(self):
        Wallet.objects.create(user=self.user_seller, balance=500)
        self.client.force_login(self.user)
        response = self.client.post(reverse('order-payment', kwargs={'pk': self.order.pk}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_pay_when_seller_has_no_wallet(self):
        Wallet.objects.create(user=self.user, balance=500)
        self.client.force_login(self.user)
        response = self.client.post(reverse('order-payment', kwargs={'pk': self.order.pk}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_pay_when_user_has_no_money(self):
        Wallet.objects.create(user=self.user_seller, balance=500)
        Wallet.objects.create(user=self.user, balance=0)
        self.client.force_login(self.user)
        response = self.client.post(reverse('order-payment', kwargs={'pk': self.order.pk}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_pay_when_all_ok(self):
        Wallet.objects.create(user=self.user_seller, balance=500)
        Wallet.objects.create(user=self.user, balance=500)
        self.client.force_login(self.user)
        response = self.client.post(reverse('order-payment', kwargs={'pk': self.order.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_pay_when_order_is_paid(self):
        Wallet.objects.create(user=self.user_seller, balance=500)
        Wallet.objects.create(user=self.user, balance=500)
        self.order.payment_status = True
        self.order.save()
        self.client.force_login(self.user)
        response = self.client.post(reverse('order-payment', kwargs={'pk': self.order.pk}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
