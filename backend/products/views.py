import django_filters
from api.authentication import TokenAuthentication
from api.mixins import (
    IsObjectOwnerPermission,
    StaffEditorPermissionMixin,
    UserQuerySetMixin,
)
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import authentication
from rest_framework.filters import SearchFilter
from rest_framework.generics import (
    DestroyAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated

from .models import Product
from .serializers import ProductSerializer


class ProductFilter(django_filters.FilterSet):
    quantity_lte = django_filters.rest_framework.filters.NumberFilter(field_name='quantity', lookup_expr='lte')
    quantity_gte = django_filters.rest_framework.filters.NumberFilter(field_name='quantity', lookup_expr='gte')

    class Meta:
        model = Product
        fields = ['quantity', 'quantity_lte', 'quantity_gte']


@method_decorator(cache_page(30), name='get', )
class ProductListCreateAPIView(
    # StaffEditorPermissionMixin,
    # UserQuerySetMixin,
    ListCreateAPIView
):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [authentication.SessionAuthentication, TokenAuthentication]
    allow_staff_view = False
    filter_backends = [SearchFilter, django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = ProductFilter
    search_fields = ('title', 'content')

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.validated_data.get('title')
        content = serializer.validated_data.get('content', 'blank')
        serializer.save(content=content, user=self.request.user)


@method_decorator(cache_page(30), name='get_queryset')
class ProductListMyAPIView(
    UserQuerySetMixin,
    ListCreateAPIView
):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    def get_queryset(self):
        queryset = Product.objects.filter(user=self.request.user)
        return queryset


@method_decorator(cache_page(30), name='get')
class ProductDetailAPIView(
    UserQuerySetMixin,
    RetrieveAPIView
):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    allow_staff_view = True


class ProductDeleteAPIView(
    StaffEditorPermissionMixin,
    UserQuerySetMixin,
    DestroyAPIView
):
    queryset = Product.objects.all()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)


class ProductUpdateAPIView(
        UserQuerySetMixin,
        UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'pk'
    permission_classes = [IsAuthenticated, IsObjectOwnerPermission]

    def perform_update(self, serializer):
        instance = serializer.save()
        if not instance.content:
            instance.content = 'blank content'

# @api_view(['GET', 'POST'])
# def alt_product_view(request, pk=None, *args, **kwargs):
#
#     method = request.method
#
#     if method == 'GET':
#         if pk is not None:
#             obj = get_object_or_404(Product, pk=pk)
#             data = ProductSerializer(obj, many=False).data
#             return Response(data)
#
#         qs = Product.objects.all()
#         data = ProductSerializer(qs, many=True).data
#         return Response(data, status=status.HTTP_200_OK)
#
#     if method == 'POST':
#
#         serializer = ProductSerializer(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             title = serializer.validated_data.get('title')
#             content = serializer.validated_data.get('content', None)
#             if content is None:
#                 serializer.save(content=title)
#             serializer.save(content=content)
#             return Response(serializer.data)
#
#         return Response({"error": "Not allowed", "message": "not good data"}, status=status.HTTP_400_BAD_REQUEST)
