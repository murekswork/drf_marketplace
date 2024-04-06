from delivery.models import Delivery
from delivery.serializers import DeliverySerializer
from rest_framework.generics import RetrieveAPIView


class DeliveryApiView(RetrieveAPIView):
    lookup_field = 'pk'
    queryset = Delivery.objects.all().select_related('courier')
    serializer_class = DeliverySerializer
