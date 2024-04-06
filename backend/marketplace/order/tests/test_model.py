from django.contrib.auth import get_user_model
from django.test import TestCase
from order.models import Order
from order.services.order_service import OrderServiceFactory
from products.models import Product
from shop.models import Shop
from wallet.models import Wallet


class OrderModelTestCase(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create(
            username="test", email="test@test.com"
        )
        self.user.set_password("0xABAD1DEA")
        self.user_wallet = Wallet.objects.create(user=self.user, balance=100000)
        self.shop = Shop.objects.create(
            user=self.user, title="shoptitle", description="shopdescription"
        )
        self.order_product = Product.objects.create(
            shop=self.shop, title="product", price=100
        )
        self.order = Order.objects.create(
            user=self.user, product=self.order_product, count=5
        )

    def test_product_field(self):
        self.assertEqual(self.order.product, self.order_product)

    def test_user_field(self):
        self.assertEqual(self.order.user, self.user)

    def test_count_field(self):
        self.assertEqual(self.order.count, 5)

    def test_amount_field(self):
        self.assertEqual(int(self.order.amount), 0)

    def test_total_amount_property(self):
        self.assertEqual(
            float(self.order.total_amount),
            float(self.order_product.price * self.order.count),
        )

    def test_payment_status_field(self):
        self.assertEqual(self.order.payment_status, False)

    def test_payment_status_field_when_payed(self):
        self.order_product.quantity = 50
        self.order_product.save()
        service = OrderServiceFactory.get_order_service(self.order)
        service.pay_order()
        self.assertEqual(self.order.payment_status, True)


class OrderModelSaveMethodTestCase(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test", email="test@mail.com"
        )
        self.shop = Shop.objects.create(
            user=self.user, title="title", description="description"
        )
        self.product = Product.objects.create(
            shop=self.shop, title="title", public=True, content="content", quantity=5
        )
        self.order = Order.objects.create(product=self.product, count=3, user=self.user)

    def test_order_model_when_create_not_paid_then_product_sales_count_not_increases(
        self,
    ):
        self.assertTrue(self.product.sales_count == 0)

    def test_order_model_when_create_and_paid_then_product_sales_count_increases(self):
        self.order.payment_status = True
        self.order.save()
        self.product.refresh_from_db()
        self.assertTrue(self.product.sales_count == 1)

    def test_order_model_when_create_and_paid_second_then_product_sales_count_increases(
        self,
    ):
        self.order2 = Order.objects.create(
            product=self.product, count=3, user=self.user
        )
        self.order.payment_status = True
        self.order.save()
        self.order2.payment_status = True
        self.order2.save()
        self.product.refresh_from_db()
        self.assertTrue(self.product.sales_count == 2)
