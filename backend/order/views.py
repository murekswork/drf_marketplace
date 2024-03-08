import datetime

import django_filters
from api.mixins import UserQuerySetMixin
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from .mixins import OrderServiceFabricMixin
from .models import Order
from .serialziers import OrderSerializer


class OrderListCreateAPIView(UserQuerySetMixin, generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    allow_staff_view = False
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['payment_status']

    def get_queryset(self):
        qs = self.queryset
        qs = (qs.filter(Q(lifetime__gte=datetime.datetime.now()) | Q(payment_status=True)).
              select_related('user', 'product').prefetch_related('product__sales'))
        return qs

    def perform_create(self, serializer):
        product_user = serializer.validated_data['product_pk'].shop.user
        if product_user != self.request.user:
            super().perform_create(serializer)
        else:
            raise APIException('You can not buy your own product!')


class OrderPayAPIView(UserQuerySetMixin, OrderServiceFabricMixin, generics.RetrieveAPIView):
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def post(self, request, *args, **kwargs):
        # print(request.user, request.user.wallet, 'Its users wallet!')
        service = self.order_fabric.get_order_service(order=self.get_object())

        payment = service.pay_order()
        if payment.get('success') is True:
            return Response('Payment successfully completed!')
        else:
            return Response(payment.get('message'), status=status.HTTP_400_BAD_REQUEST)
