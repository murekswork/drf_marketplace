from order.models import Order
from rest_framework.exceptions import ValidationError
from wallet.models import Wallet


class OrderValidationService:

    # TODO: Think about segregation this class to different ones for ex. ProductValidation, WalletValidation, etc...

    def __init__(self, order: Order) -> None:
        self.order = order

    def _validate_product_quantity(self) -> dict[str, bool | str]:
        product_quantity = self.order.product.quantity
        if product_quantity >= self.order.count:
            return {"success": True}
        else:
            return {
                "success": False,
                "message": "Product does not have enough quantity now!",
            }

    def _validate_users_wallet(self) -> dict[str, bool | str]:
        wallet_exist = Wallet.objects.filter(user=self.order.user).exists()
        if wallet_exist is True:
            return {"success": True}
        else:
            return {"success": False, "message": "Customer does not have wallet!"}

    def _validate_user_has_enough_money(self) -> dict[str, bool | str]:
        wallet_balance = self.order.user.wallet.balance
        if wallet_balance >= self.order.amount:
            return {"success": True}
        else:
            return {"success": False, "message": "Customer does not have enough money!"}

    def _validate_order_positive_amount(self) -> dict[str, bool | str]:
        if self.order.amount > 0:
            return {"success": True}
        else:
            return {
                "success": False,
                "message": "Order amount could not be less than 0!",
            }

    def _validate_order_is_not_paid(self) -> dict[str, bool | str]:
        if self.order.payment_status is True:
            return {"success": False, "message": "Order is already paid!"}
        return {"success": True}

    def validate_order(self) -> dict[str, bool | str]:
        """Interface method to run all necessary validations for order, if all pass then order could be paid"""
        for method in self.__dir__():
            if "_validate_" in method:
                validation = getattr(self, method)()
                if validation != {"success": True}:
                    raise ValidationError(validation.get("message"))
        return {"success": True}
