from api.mixins import UserQuerySetMixin
from products.models import Product
from products.serializers import ProductSerializer
from rest_framework import generics
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated


class SearchListView(UserQuerySetMixin, generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    allow_staff_view = True
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset()
        q = self.request.GET.get('search')
        result = Product.objects.none()
        if q is not None:
            result = qs.search(q)
        return result.prefetch_related('articles', 'sales', 'orders', 'shop')
