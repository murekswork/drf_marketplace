import datetime
from abc import ABC, abstractmethod

from django.conf import settings
from django.db import transaction
from rest_framework.exceptions import ValidationError

from order.models import Order
from products.models import Product, Sale
from wallet.models import Wallet


class OrderValidationService:

    def __init__(self, order: Order) -> None:
        self.order = order

    def _validate_product_quantity(self) -> dict[str, bool | str]:
        product = self.order.product
        if product.quantity >= self.order.count:
            return {'success': True}
        else:
            return {'success': False, 'message': 'Product does not have enough quantity now!'}

    def _validate_users_wallet(self) -> dict[str, bool]:
        wallet_exist = Wallet.objects.filter(user=self.order.user).exists()
        if wallet_exist is True:
            return {'success': True}
        else:
            return {'success': False, 'message': 'Customer does not have wallet!'}

    def _validate_user_has_enough_money(self):
        if self.order.user.wallet.balance >= self.order.amount:
            return {'success': True}
        else:
            return {'success': False, 'message': 'Customer does not have enough money!'}

    def _validate_order_positive_amount(self):
        if self.order.amount > 0:
            return {'success': True}
        else:
            return {'success': False, 'message': 'Order amount could not be less than 0!'}

    def _validate_order_is_not_paid(self):
        if self.order.payment_status is True:
            return {'success': False, 'message': 'Order is already paid!'}
        return {'success': True}

    def validate_order(self) -> dict[str, bool | str]:
        quantity_validation = self._validate_product_quantity()

        if quantity_validation != {'success': True}:
            raise ValidationError(quantity_validation.get('message'))

        customer_wallet_validation = self._validate_users_wallet()
        if customer_wallet_validation != {'success': True}:
            raise ValidationError(customer_wallet_validation.get('message'))

        customer_balance_validation = self._validate_user_has_enough_money()
        if customer_balance_validation != {'success': True}:
            raise ValidationError(customer_wallet_validation.get('message'))

        order_positive_amount_validation = self._validate_order_positive_amount()
        if order_positive_amount_validation != {'success': True}:
            raise ValidationError(order_positive_amount_validation.get('message'))

        return {'success': True}


class SaleValidationService:

    def __init__(self, sale: Sale):
        self.sale = sale

    def validate_sale_expired(self) -> dict[str, bool | str]:
        if self.sale.end_date > datetime.datetime.now():
            return {'success': True}
        return {'success': False, 'message': 'Sale is expired!'}


class OrderPaymentService:

    def __init__(self, order: Order) -> None:
        self.order = order

    @transaction.atomic()
    def _make_payment_transaction(self, order_amount) -> dict[str, bool | str]:
        self.order.user.wallet.balance = float(self.order.user.wallet.balance) - order_amount
        self.order.product.shop.user.wallet.balance = float(
            self.order.product.shop.user.wallet.balance) + order_amount
        self.order.product.quantity -= self.order.count
        self.order.payment_status = True
        self.order.amount = order_amount

        self.order.user.wallet.save()
        self.order.product.shop.user.wallet.save()
        self.order.save()

        return {'success': True}

    def pay_order(self) -> dict[str, str | bool]:
        # self.validate_users_wallet(user=self._user)
        # order_amount = self.get_order_amount()

        # if self._user.wallet.balance < order_amount:
        #     return {'success': False, 'message': 'user does not have enough money'}

        # quantity_validation = self.validate_product_quantity()

        # if quantity_validation['success'] is False:
        #     return quantity_validation
        try:
            return self._make_payment_transaction(float(self.order.amount))
        except Exception as e:
            return {'success': False, 'message': f'some troubles with transaction! {e}'}


class AbstractOrderService(ABC):

    def __init__(
            self,
            user: settings.AUTH_USER_MODEL,
            order: Order,
            # payment_service: OrderPaymentService,
            # validation_service: OrderValidationService
    ) -> None:
        self.user = user
        self.order: Order = order
        self._product: Product = order.product
        self._order_amount = None
        self.payment_service = OrderPaymentService(self.order)
        self.validation_service = OrderValidationService(self.order)

    @abstractmethod
    def get_order_amount(self):
        raise NotImplementedError

    @abstractmethod
    def pay_order(self):
        raise NotImplementedError


class SimpleOrderService(AbstractOrderService):

    def pay_order(self):
        self.get_order_amount()
        validation = self.validation_service.validate_order()

        if validation != {'success': True}:
            return ValidationError()

        payment = self.payment_service.pay_order()
        return payment

    def get_order_amount(self) -> None:
        self.order.amount = float(self.order.product.price) * self.order.count
        self.order.save()
        self.order.refresh_from_db()


class SaleOrderService(SimpleOrderService):

    def __init__(self, user: settings.AUTH_USER_MODEL, order: Order, sale: Sale):
        super().__init__(user, order)
        self.sale = sale
        self.sale_validation_service = SaleValidationService(sale=self.sale)

    def get_order_amount(self) -> None:
        sale_validation = self.sale_validation_service.validate_sale_expired()
        if sale_validation != {'success': True}:
            return super().get_order_amount()

        product_price_with_sale = self.order.product.price - (self.order.product.price * self.sale.size / 100)
        self.order.amount = float(product_price_with_sale) * float(self.order.count)
        self.order.save()
        self.order.refresh_from_db()


class OrderServiceFactory:

    @staticmethod
    def get_order_service(order):
        sale = OrderServiceFactory.check_sale(order.product)
        if sale:
            order_service = SaleOrderService(user=order.user, order=order, sale=sale)
        else:
            order_service = SimpleOrderService(user=order.user, order=order)

        return order_service

    @staticmethod
    def check_sale(product):
        sale: Sale = product.sales.filter(end_date__gte=datetime.datetime.now()).first()
        if sale:
            return sale
