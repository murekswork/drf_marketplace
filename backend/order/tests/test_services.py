from django.contrib.auth import get_user_model
from django.test import TestCase
from order.models import Order
from order.services.order_service import (
    OrderServiceFabric,
    SaleOrderService,
    SimpleOrderService,
)
from products.models import Product, Sale
from rest_framework.exceptions import ValidationError
from wallet.models import Wallet


class TestOrderServiceFabric(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create(username='test', email='test@test.com')
        self.user.set_password('0xABAD1DEA')
        self.user.save()
        self.user_wallet = Wallet.objects.create(user=self.user, balance=100000)
        self.order_product = Product.objects.create(user=self.user, title='product', price=100)
        self.order = Order.objects.create(user=self.user, product=self.order_product, count=1)

    def test_order_service_fabric_create_right_service_when_not_sale(self):
        service_fabric = OrderServiceFabric()
        service = service_fabric.get_order_service(order=self.order)
        self.assertEqual(service.__class__, SimpleOrderService)

    def test_order_service_fabric_create_right_service_when_sale(self):
        service_fabric = OrderServiceFabric()
        Sale.objects.create(product=self.order_product, size=50)
        service = service_fabric.get_order_service(order=self.order)
        self.assertEqual(service.__class__, SaleOrderService)


class TestSimpleOrderService(TestCase):

    def setUp(self):
        self.user_with_wallet = get_user_model().objects.create(username='test', email='test@test.com')
        self.user_with_wallet.set_password('0xABAD1DEA')
        self.user_with_wallet.save()
        self.user_wallet = Wallet.objects.create(user=self.user_with_wallet, balance=100000)
        self.order_product = Product.objects.create(user=self.user_with_wallet, title='product', price=100)
        self.order = Order.objects.create(user=self.user_with_wallet, product=self.order_product, count=5)
        self.user_without_wallet = get_user_model().objects.create(username='test1', email='test1@email.com')
        self.user_without_wallet.set_password('0xABAD1DEA')
        self.user_without_wallet.save()
        self.order_without_wallet = Order.objects.create(user=self.user_without_wallet, product=self.order_product,
                                                         count=5)

    def test_simple_order_validate_users_wallet_when_no_wallet(self):
        service_factory = OrderServiceFabric()
        service = service_factory.get_order_service(order=self.order_without_wallet)
        with self.assertRaises(ValidationError):
            service.validate_users_wallet(self.user_without_wallet)

    def test_simple_order_validate_users_wallet_when_wallet(self):
        service_factory = OrderServiceFabric()
        service = service_factory.get_order_service(order=self.order)
        self.assertEqual(service.validate_users_wallet(self.user_with_wallet), None)

    def test_order_service_pay_order_when_user_balance_lt_order_amount(self):
        order = self.order
        order.amount = 5000
        self.user_wallet.balance = 100
        service = SimpleOrderService(user=self.user_with_wallet, order=self.order)
        self.assertEqual(service.pay_order()['success'], False)

    def test_order_service_pay_order_when_product_quantity_lt_order_count(self):
        self.order_product.quantity = 1
        self.order_product.save()
        self.order.count = 50
        self.order.save()
        service = SimpleOrderService(user=self.user_with_wallet, order=self.order)
        self.assertEqual(service.pay_order()['success'], False)

    def test_order_service_pay_order_when_wallet_balance_changed_after_order_service_created(self):
        self.order_product.quantity = 5
        self.order_product.save()
        self.user_wallet.balance = 600
        self.user_wallet.save()
        service = SimpleOrderService(user=self.user_with_wallet, order=self.order)
        self.user_wallet.balance = 0
        self.assertEqual(float(service.get_order_amount()), 500)
        self.assertEqual(service.pay_order()['success'], False)

    def test_order_service_pay_order_charges_right_amount(self):
        user_buyer = get_user_model().objects.create_user(username='buyer', email='buyer@email.com')
        user_buyer.set_password('afjsoff1412')
        user_buyer.save()
        user_buyer_wallet = Wallet.objects.create(user=user_buyer, balance=50000)
        self.order_product.quantity = 20
        self.order_product.save()

        seller_wallet_before_payment = self.user_wallet.balance
        buyer_wallet_before_payment = user_buyer_wallet.balance
        order = Order.objects.create(user=user_buyer, product=self.order_product, count=1)
        service = SimpleOrderService(user=user_buyer, order=order)

        service.pay_order()
        self.assertEqual(float(self.user_wallet.balance),
                         float(seller_wallet_before_payment) + float(self.order_product.price))
        self.assertEqual(float(user_buyer_wallet.balance),
                         float(buyer_wallet_before_payment) - float(self.order_product.price))


class TestSaleOrderService(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test3', email='test3@email.com')
        self.user.set_password('0xABAD1DEA')
        self.product = Product.objects.create(title='PRODUCT', content='PRODUCTS CONTENT', price=20, quantity=50,
                                              user=self.user)
        self.order = Order.objects.create(product=self.product, user=self.user, count=1)
        self.sale = Sale.objects.create(product=self.product, size=50)
        self.user_wallet = Wallet.objects.create(user=self.user, balance=1000)

    def test_order_sale_service_return_right_amount(self):
        service = SaleOrderService(user=self.user, order=self.order, sale=self.sale)
        self.assertEqual(float(service.get_order_amount()), float(10))

    def test_order_sale_service_charges_right_amount(self):
        user_buyer = get_user_model().objects.create_user(username='buyer', email='buyer@email.com')
        user_buyer.set_password('afjsoff1412')
        user_buyer.save()
        user_buyer_wallet = Wallet.objects.create(user=user_buyer, balance=1000)
        self.product.quantity = 20
        self.product.save()

        seller_wallet_before_payment = self.user_wallet.balance
        buyer_wallet_before_payment = user_buyer_wallet.balance
        order = Order.objects.create(user=user_buyer, product=self.product, count=1)
        service = SaleOrderService(user=user_buyer, order=order, sale=self.sale)

        service.pay_order()
        self.assertEqual(float(self.user_wallet.balance),
                         float(seller_wallet_before_payment) + float(10))

        self.assertEqual(float(user_buyer_wallet.balance),
                         float(buyer_wallet_before_payment) - float(10))
