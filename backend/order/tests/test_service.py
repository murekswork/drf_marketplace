import datetime
import logging

from django.contrib.auth import get_user_model
from django.test import TestCase
from order.models import Order
from order.services.order_service import (
    OrderValidationService,
    SaleOrderService,
    SimpleOrderService,
)
from products.models import Product, Sale
from rest_framework.exceptions import ValidationError
from shop.models import Shop
from wallet.models import Wallet


class OrderValidationServiceTestCase(TestCase):

    def setUp(self):
        self.user_seller = get_user_model().objects.create_user(
            username='seller',
            email='seller_mail@mail.com'
        )

        self.user_buyer = get_user_model().objects.create_user(
            username='buyer',
            email='buyer_mail@mail.com'
        )

        self.shop = Shop.objects.create(
            title='Shop', description='Shop description', user=self.user_seller
        )

        self.product = Product.objects.create(
            title='Product', content='Product description', shop=self.shop
        )

        self.order = Order.objects.create(
            product=self.product, user=self.user_buyer, count=5
        )

    def test_order_validation_service_validate_product_quantity_when_quantity_less_than_count(self):
        self.product.quantity = 0
        self.product.save()
        self.order.count = 1
        self.order.save()
        service = OrderValidationService(order=self.order)
        result = service._validate_product_quantity()
        self.assertEqual(result, {'success': False, 'message': 'Product does not have enough quantity now!'})

    def test_order_validation_service_validate_product_quantity_when_quantity_more_than_count(self):
        self.product.quantity = 2
        self.product.save()
        self.order.count = 1
        self.order.save()
        service = OrderValidationService(order=self.order)
        result = service._validate_product_quantity()
        self.assertEqual(result, {'success': True})

    def test_order_validation_service_validate_product_quantity_when_quantity_equal_to_count(self):
        self.product.quantity = 1
        self.product.save()
        self.order.count = 1
        self.order.save()
        service = OrderValidationService(order=self.order)
        result = service._validate_product_quantity()
        self.assertEqual(result, {'success': True})

    def test_order_validation_service_validate_users_wallet_when_wallet_does_not_exist(self):
        service = OrderValidationService(order=self.order)
        result = service._validate_users_wallet()
        self.assertEqual(result, {'success': False, 'message': 'Customer does not have wallet!'})

    def test_order_validation_service_validate_users_wallet_when_wallet_exist(self):
        Wallet.objects.create(user=self.user_buyer, balance=0)
        service = OrderValidationService(order=self.order)
        result = service._validate_users_wallet()
        self.assertEqual(result, {'success': True})

    def test_order_validation_service__validate_user_has_enough_money_when_does_not_have_enough_money(self):
        self.order.amount = 100
        Wallet.objects.create(user=self.user_buyer, balance=0)
        service = OrderValidationService(order=self.order)
        result = service._validate_user_has_enough_money()
        self.assertEqual(result, {'success': False, 'message': 'Customer does not have enough money!'})

    def test_order_validation_service__validate_user_has_enough_money_when_have_enough_money(self):
        self.order.amount = 100
        Wallet.objects.create(user=self.user_buyer, balance=101)
        service = OrderValidationService(order=self.order)
        result = service._validate_user_has_enough_money()
        self.assertEqual(result, {'success': True})

    def test_order_validation_service__validate_user_has_enough_money_when_have_equal_money(self):
        self.order.amount = 100
        Wallet.objects.create(user=self.user_buyer, balance=100)
        service = OrderValidationService(order=self.order)
        result = service._validate_user_has_enough_money()
        self.assertEqual(result, {'success': True})

    def test_order_validation_service__validate_order_positive_amount_when_order_amount_is_positive(self):
        self.order.amount = 100
        Wallet.objects.create(user=self.user_buyer, balance=100)
        service = OrderValidationService(order=self.order)
        result = service._validate_order_positive_amount()
        self.assertEqual(result, {'success': True})

    def test_order_validation_service__validate_order_positive_amount_when_order_amount_is_negative(self):
        self.order.amount = -100
        Wallet.objects.create(user=self.user_buyer, balance=100)
        service = OrderValidationService(order=self.order)
        result = service._validate_order_positive_amount()
        self.assertEqual(result, {'success': False, 'message': 'Order amount could not be less than 0!'})

    def test_order_validation_service_validate_order_when_all_ok(self):
        self.product.quantity = 2
        Wallet.objects.create(user=self.user_buyer, balance=101)
        self.order.count = 1
        self.order.amount = 100
        service = OrderValidationService(order=self.order)
        result = service.validate_order()
        self.assertEqual(result, {'success': True})

    def test_order_validation_service_validate_order_is_not_paid_when_order_is_not_paid(self):
        self.order.payment_status = False
        service = OrderValidationService(order=self.order)
        result = service._validate_order_is_not_paid()
        self.assertEqual(result, {'success': True})

    def test_order_validation_service_validate_order_is_not_paid_when_order_is_paid(self):
        self.order.payment_status = True
        service = OrderValidationService(order=self.order)
        result = service._validate_order_is_not_paid()
        self.assertEqual(result, {'success': False, 'message': 'Order is already paid!'})


class SimpleOrderServiceTestCase(TestCase):

    def setUp(self):
        self.user_seller = get_user_model().objects.create_user(
            username='seller',
            email='seller_mail@mail.com'
        )

        self.user_buyer = get_user_model().objects.create_user(
            username='buyer',
            email='buyer_mail@mail.com'
        )

        self.shop = Shop.objects.create(
            title='Shop', description='Shop description', user=self.user_seller
        )

        self.product = Product.objects.create(
            title='Product', content='Product description', shop=self.shop
        )

        self.order = Order.objects.create(
            product=self.product, user=self.user_buyer, count=5
        )

    def test_simple_order_service_get_order_amount(self):
        self.order.count = 5
        self.product.price = 100
        service = SimpleOrderService(order=self.order, user=self.user_buyer)
        service.get_order_amount()
        self.assertEqual(self.order.amount, 500)

    def test_simple_order_service_pay_order_when_raise_some_error(self):
        self.order.count = 5
        self.product.price = 100
        service = SimpleOrderService(order=self.order, user=self.user_buyer)
        with self.assertRaises(ValidationError):
            service.pay_order()

    def test_simple_order_service_pay_order_when_all_ok(self):
        self.order.count = 5
        self.product.quantity = 6
        self.product.save()
        self.product.price = 1
        Wallet.objects.create(user=self.user_buyer, balance=500)
        service = SimpleOrderService(order=self.order, user=self.user_buyer)
        result = service.pay_order()
        self.assertTrue(result, 'payment completed')


class SaleOrderServiceTestCase(TestCase):

    def setUp(self):
        self.user_seller = get_user_model().objects.create_user(
            username='seller',
            email='seller_mail@mail.com'
        )

        self.user_buyer = get_user_model().objects.create_user(
            username='buyer',
            email='buyer_mail@mail.com'
        )

        self.shop = Shop.objects.create(
            title='Shop', description='Shop description', user=self.user_seller
        )

        self.product = Product.objects.create(
            title='Product', content='Product description', shop=self.shop
        )

        self.order = Order.objects.create(
            product=self.product, user=self.user_buyer, count=5
        )

    def test_sale_order_service_get_order_amount_when_sale_is_active(self):
        sale = Sale.objects.create(product=self.product, size=50)
        self.order.count = 5
        self.product.price = 100
        service = SaleOrderService(order=self.order, user=self.user_buyer, sale=sale)
        service.get_order_amount()
        self.assertEqual(self.order.amount, 250)

    def test_sale_order_service_get_order_amount_when_sale_is_expired(self):
        sale = Sale.objects.create(product=self.product, size=50,
                                   end_date=datetime.datetime.now() - datetime.timedelta(days=10))
        self.order.count = 5
        self.product.price = 100
        service = SaleOrderService(order=self.order, user=self.user_buyer, sale=sale)
        service.get_order_amount()
        logging.warning(f'{sale.end_date}, {datetime.datetime.now() - datetime.timedelta(days=10)}')
        self.assertEqual(self.order.amount, 500)

    def test_sale_order_service_get_order_amount_when_sale_is_expired_after_order_created(self):
        sale = Sale.objects.create(product=self.product, size=50)
        self.order.count = 5
        self.product.price = 100
        service = SaleOrderService(order=self.order, user=self.user_buyer, sale=sale)
        sale.end_date = datetime.datetime.now() - datetime.timedelta(days=10)
        service.get_order_amount()
        logging.warning(f'{sale.end_date}, {datetime.datetime.now() - datetime.timedelta(days=10)}')
        self.assertEqual(self.order.amount, 500)

    # TODO: Write test case for OrderServiceFactory
