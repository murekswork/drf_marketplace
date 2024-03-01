import datetime

from api.mixins import UserQuerySetMixin
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.response import Response

from .mixins import OrderServiceFabricMixin
from .models import Order
from .serialziers import OrderSerializer


class OrderListCreateAPIView(UserQuerySetMixin, generics.ListCreateAPIView):

    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    allow_staff_view = False

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(Q(lifetime__gte=datetime.datetime.now()) | Q(payment_status=True))
        return qs


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
