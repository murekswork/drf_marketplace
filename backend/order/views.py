import datetime

import django_filters
from api.mixins import UserQuerySetMixin
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.response import Response

from .mixins import OrderServiceFabricMixin
from .models import Order
from .serialziers import OrderCreateSerializer, OrderSerializer


class OrderListCreateAPIView(
    UserQuerySetMixin,
    generics.ListCreateAPIView
):
    serializer_class = OrderSerializer
    queryset = Order.objects.filter(Q(lifetime__gte=datetime.datetime.now()) | Q(payment_status=True)).select_related(
        'user', 'product').prefetch_related('product__sales').order_by('-created_at')
    allow_staff_view = False
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['payment_status']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return super().get_serializer_class()


class OrderPayAPIView(
    UserQuerySetMixin,
    OrderServiceFabricMixin,
    generics.RetrieveAPIView
):
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def post(self, request, *args, **kwargs):
        service = self.order_fabric.get_order_service(order=self.get_object())

        payment = service.pay_order()
        if payment.get('success') is True:
            return Response('Payment successfully completed!')
        else:
            return Response(payment.get('message'), status=status.HTTP_400_BAD_REQUEST)
