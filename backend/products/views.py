import django_filters
from api.authentication import TokenAuthentication
from api.mixins import UserQuerySetMixin
from rest_framework import authentication, status
from rest_framework.filters import SearchFilter
from rest_framework.generics import (
    DestroyAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    get_object_or_404,
)
from rest_framework.response import Response
from shop.models import Shop
from shop.permissions import ProductShopStaffPermission

from .models import Product
from .serializers import (
    ProductSerializer,
    ProductSerializerFull,
    ProductUpdateSerializer,
)


class ProductFilter(django_filters.FilterSet):
    quantity_lte = django_filters.rest_framework.filters.NumberFilter(field_name='quantity', lookup_expr='lte')
    quantity_gte = django_filters.rest_framework.filters.NumberFilter(field_name='quantity', lookup_expr='gte')

    class Meta:
        model = Product
        fields = ['quantity', 'quantity_lte', 'quantity_gte']


class ProductListCreateAPIView(
    ListCreateAPIView
):
    queryset = (Product.objects.filter(public=True).prefetch_related('articles', 'sales', 'orders').select_related())
    serializer_class = ProductSerializer
    authentication_classes = [authentication.SessionAuthentication, TokenAuthentication]
    allow_staff_view = False
    filter_backends = [SearchFilter, django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = ProductFilter
    search_fields = ('title', 'content')

    def post(self, request, *args, **kwargs):
        # TODO: REWRITE THIS MAYBE
        shop = get_object_or_404(Shop, id=int(request.data.get('shop', '0')))
        if request.user.is_authenticated:
            user_role = shop.managers.through.objects.filter(user=request.user)
            if user_role.exists():
                user_role = user_role.all()[0]
                if user_role.has_permission('create_shop_product'):
                    return super().post(request, *args, **kwargs)

        return Response({'You dont have permission to upload products in this shop'}, status=status.HTTP_403_FORBIDDEN)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.validated_data.get('title')
        content = serializer.validated_data.get('content', 'blank')
        serializer.save(content=content)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response('Your product will be published after short check up!',
                        status=status.HTTP_201_CREATED, headers=headers)


class ProductListMyAPIView(
    UserQuerySetMixin,
    ListCreateAPIView
):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    def get_queryset(self):
        queryset = Product.objects.filter(user=self.request.user)
        return queryset


class ProductDetailAPIView(
    RetrieveAPIView
):
    queryset = Product.objects.filter(public=True).prefetch_related('articles', 'sales', 'shop')
    serializer_class = ProductSerializerFull
    allow_staff_view = True


class ProductDeleteAPIView(
    DestroyAPIView
):
    queryset = Product.objects.all()
    permission_classes = [ProductShopStaffPermission]
    lookup_field = 'pk'


class ProductUpdateAPIView(
    UpdateAPIView
):
    queryset = Product.objects.all()
    serializer_class = ProductUpdateSerializer
    lookup_field = 'pk'
    permission_classes = [ProductShopStaffPermission]

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
