from courier.models import Courier
from delivery.models import Delivery


class CourierDeliveryService:

    def _confirm_delivery(self, delivery: Delivery) -> Courier:
        c = delivery.courier
        c.done_deliveries += 1
        c.balance = delivery.amount + float(c.balance)
        c.rank += 0.1
        c.save()
        return c

    def _cancel_delivery(self, delivery: Delivery):
        c = delivery.courier
        c.balance = float(c.balance) - delivery.amount
        c.rank -= 0.3
        c.save()
        return c

    def close_delivery(self, delivery: Delivery) -> Courier:
        c = None
        if delivery.status == 5:
            c = self._confirm_delivery(delivery)
        elif delivery.status == 0:
            c = self._cancel_delivery(delivery)
        return c
