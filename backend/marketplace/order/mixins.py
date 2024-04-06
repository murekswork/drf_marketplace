from order.services.order_service import OrderServiceFactory


class OrderServiceFabricMixin:

    order_fabric = OrderServiceFactory
