from django.db import transaction
from order.models import Order


class OrderPaymentService:

    def __init__(self, order: Order) -> None:
        self.order = order

    @transaction.atomic()
    def _make_payment_transaction(self, order_amount) -> dict[str, bool | str]:
        self.order.user.wallet.balance = (
            float(self.order.user.wallet.balance) - order_amount
        )
        self.order.product.shop.user.wallet.balance = (
            float(self.order.product.shop.user.wallet.balance) + order_amount
        )
        self.order.product.quantity -= self.order.count
        self.order.payment_status = True
        self.order.amount = order_amount

        self.order.user.wallet.save()
        self.order.product.shop.user.wallet.save()
        self.order.save()

        return {"success": True}

    def pay_order(self) -> dict[str, str | bool]:
        try:
            return self._make_payment_transaction(float(self.order.amount))
        except Exception as e:
            return {"success": False, "message": f"Some troubles with transaction! {e}"}
