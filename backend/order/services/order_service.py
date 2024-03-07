from abc import ABC, abstractmethod

from django.conf import settings
from django.db import transaction
from order.models import Order
from products.models import Product, Sale
from rest_framework.exceptions import ValidationError
from wallet.models import Wallet


class AbstractOrderService(ABC):

    def __init__(self, user: settings.AUTH_USER_MODEL, order: Order) -> None:
        self._user = user
        self._product: Product = order.product
        self._order: Order = order
        self._order_amount = 50

    def validate_users_wallet(self, user: settings.AUTH_USER_MODEL) -> None:
        wallet = Wallet.objects.filter(user=user).exists()
        if wallet is True:
            self._user = user
        else:
            raise ValidationError('User does not have wallet!')

    def validate_product_quantity(self):
        product = Product.objects.get(pk=self._product.pk)
        if product.quantity >= self._order.count:
            return {'success': True}
        else:
            return {'success': False, 'message': 'Product does not have enough quantity now!'}

    @abstractmethod
    def create_order(self, count: int):
        raise NotImplementedError

    @abstractmethod
    def pay_order(self):
        raise NotImplementedError


class SimpleOrderService(AbstractOrderService):

    def get_order_amount(self):
        self._order_amount = float(self._product.price) * self._order.count
        return self._order_amount

    def create_order(self, count):
        order = Order.objects.create(
            user=self._user,
            product=self._product,
            count=count
        )
        return order

    @transaction.atomic()
    def _pay(self, order_amount):
        self._user.wallet.balance = float(self._user.wallet.balance) - order_amount
        self._order.product.user.wallet.balance = float(self._order.product.user.wallet.balance) + order_amount
        self._order.product.quantity -= self._order.count
        self._order.payment_status = True
        self._order.amount = order_amount

        self._user.wallet.save()
        self._order.product.user.wallet.save()
        self._order.save()

        return {'success': True, 'message': 'order is paid'}

    def pay_order(self):
        if self._order.payment_status == True:
            raise ValidationError('Order already paid')
        self.validate_users_wallet(user=self._user)
        order_amount = self.get_order_amount()

        if self._user.wallet.balance < order_amount:
            return {'success': False, 'message': 'user does not have enough money'}

        quantity_validation = self.validate_product_quantity()

        if quantity_validation['success'] is False:
            return quantity_validation
        try:
            return self._pay(order_amount)
        except Exception as e:
            return {'success': False, 'message': f'some troubles with transaction! {e}'}


class SaleOrderService(SimpleOrderService):

    def __init__(self, user: settings.AUTH_USER_MODEL, order: Order, sale: Sale):
        super().__init__(user, order)
        self.sale = sale

    def get_order_amount(self):
        product_price_with_sale = self._product.price - (self._product.price * self.sale.size / 100)
        self._order_amount = float(product_price_with_sale * self._order.count)
        return self._order_amount


class OrderServiceFabric:

    @staticmethod
    def get_order_service(order):
        sale = OrderServiceFabric.check_sale(order.product)
        # order = Order.objects.create(product=product, user=user, count=count)
        if sale:
            order_service = SaleOrderService(user=order.user, order=order, sale=sale)
        else:
            order_service = SimpleOrderService(user=order.user, order=order)

        return order_service

    @staticmethod
    def check_sale(product):
        sale = product.sales.select_related().first()
        return sale
