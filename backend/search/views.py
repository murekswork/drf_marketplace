from django.db.models import Avg, Count, Q

from api.mixins import UserQuerySetMixin
from products.models import Product
from products.serializers import ProductSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


class SearchListView(UserQuerySetMixin, generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    allow_staff_view = True
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        result = Product.objects.none()
        if q is not None:
            user = None
            if self.request.user.is_authenticated:
                user = self.request.user
            result = qs.search(q, user=user)

        return (result.prefetch_related('articles', 'sales', 'orders')
                      .select_related()
                      .annotate(mark=Avg('articles__mark', default=5),
                                sales_count=Count('orders', filter=Q(orders__payment_status=True))))
