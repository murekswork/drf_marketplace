from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from order.models import Order
from order.serialziers import OrderSerializer
from products.models import Product, Sale
from wallet.models import Wallet


class OrderSerializerTestCase(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create(username='test', email='test@test.com')
        self.user.set_password('0xABAD1DEA')
        self.user.save()
        self.user_wallet = Wallet.objects.create(user=self.user, balance=100000)
        self.order_product = Product.objects.create(user=self.user, title='product', price=100)
        self.order = Order.objects.create(user=self.user, product=self.order_product, count=5)
        self.serializer = OrderSerializer(self.order)

        response = self.client.post(reverse('token-auth'),
                                    data={'username': 'test', 'password': '0xABAD1DEA'})
        self.token = response.json()['token']

        self.order_creation = self.client.post(reverse('order-list'), headers={'Authorization': f'Bearer {self.token}'},
                                               data={'product_pk': self.order_product.pk, 'count': 5})
        self.created_order = Order.objects.get(id__exact=self.order_creation.json()['id'])
        self.created_order_serializer = OrderSerializer(self.created_order)

    def test_serializer_user_field(self):
        # print(serializer.data)
        self.assertEqual(self.serializer.data['user']['username'], self.user.username)

    def test_serializer_product_field(self):
        self.assertEqual(self.serializer.data['product']['title'], self.order_product.title)

    def test_serializer_payment_url_field(self):
        self.assertEqual(self.serializer.data['payment_url'], reverse('order-payment', kwargs={'pk': self.order.pk}))

    def test_serializer_get_amount_without_product_sale(self):
        self.assertEqual(float(self.serializer.get_amount(self.order)), 0)

    def test_creation(self):
        self.assertEqual(self.order_creation.status_code, 201)

    def test_created_order_get_amount_without_sale(self):
        order = OrderSerializer(self.created_order)
        self.assertEqual(float(order.data['amount']), float(500))

    def test_created_order_get_amount_with_sale(self):
        Sale.objects.create(product=self.created_order.product, size=50)
        order = OrderSerializer(self.created_order)
        self.assertEqual(float(order.data['amount']), float(250))

    def test_created_order_get_amount_after_sale_deleted(self):
        sale = Sale.objects.create(product=self.created_order.product, size=50)
        order = OrderSerializer(self.created_order)
        self.assertEqual(float(order.data['amount']), float(250))
        sale.delete()
        order2 = OrderSerializer(self.created_order)
        self.assertEqual(float(order2.data['amount']), float(500))
