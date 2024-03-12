from abc import ABC, abstractmethod

from django.conf import settings
from django.utils import timezone
from order.models import Order
from order.services.payment.order_payment import OrderPaymentService
from order.services.validation.order_validation import OrderValidationService
from products.models import Product, Sale
from products.services.validation.sale_validation import SaleValidationService
from rest_framework.exceptions import ValidationError


class AbstractOrderService(ABC):

    def __init__(
            self,
            user: settings.AUTH_USER_MODEL,
            order: Order,
    ) -> None:
        self.user = user
        self.order: Order = order
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

    def get_order_amount(self) -> float:
        self.order.amount = float(self.order.product.price) * self.order.count
        self.order.save()
        self.order.refresh_from_db()
        return self.order.amount


class SaleOrderService(SimpleOrderService):

    def __init__(self, user: settings.AUTH_USER_MODEL, order: Order, sale: Sale):
        super().__init__(user, order)
        self.sale = sale
        self.sale_validation_service = SaleValidationService(sale=self.sale)

    def get_order_amount(self) -> float:
        sale_validation = self.sale_validation_service.validate_sale_expired()
        if sale_validation != {'success': True}:
            return super().get_order_amount()

        product_price_with_sale = self.order.product.price - (self.order.product.price * self.sale.size / 100)
        self.order.amount = float(product_price_with_sale) * float(self.order.count)
        self.order.save()
        self.order.refresh_from_db()
        return self.order.amount


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
    def check_sale(product: Product) -> Sale | None:
        sale: Sale = product.sales.filter(end_date__gte=timezone.now()).first()
        if sale:
            return sale
        return None
