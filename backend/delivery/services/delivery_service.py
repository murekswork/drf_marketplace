from abc import ABC, abstractmethod

from delivery.models import Delivery


class DeliveryFabricServiceABC(ABC):

    @abstractmethod
    def create_delivery(self, delivery_data) -> Delivery:
        raise NotImplementedError

    @abstractmethod
    def send_delivery(self, delivery: Delivery):
        raise NotImplementedError

    @abstractmethod
    def receive_delivery(self):
        raise NotImplementedError


class DeliveryService(ABC):

    def create_delivery(self, delivery_data):
        ...

    def send_delivery_to_distribution(self):
        ...
