import logging

from api.mixins import UserQuerySetMixin
from delivery.exceptions import DeliveryPickedUpException
from delivery.models import Delivery
from delivery.serializers import DeliverySerializer
from delivery.services.delivery_service import DeliveryService
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.viewsets import ModelViewSet


class DeliveryViewSet(UserQuerySetMixin, ModelViewSet):
    queryset = Delivery.objects.all().select_related('courier')
    serializer_class = DeliverySerializer
    user_field = 'order_id__user'
    http_method_names = ('get', 'patch', 'delete')

    @swagger_auto_schema(
        operation_summary='Delete delivery',
        responses={403: 'Delivery has been already picked up'},
    )
    def destroy(self, request, *args, **kwargs):
        delivery = self.get_object()
        logging.warning(f'{delivery} is DELIVERY')
        service = DeliveryService()
        try:
            service.cancel_by_customer(delivery)
        except DeliveryPickedUpException as exc:
            return JsonResponse(
                status=status.HTTP_409_CONFLICT, data={'detail': exc.args}
            )
        return JsonResponse(status=status.HTTP_204_NO_CONTENT, data={'msg': 'ok!'})
