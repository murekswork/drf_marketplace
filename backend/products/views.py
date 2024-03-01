from rest_framework import authentication
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.generics import (
    RetrieveAPIView,
    ListCreateAPIView,
    DestroyAPIView,
    UpdateAPIView,

)
from rest_framework.permissions import IsAuthenticated

from api.mixins import UserQuerySetMixin, IsObjectOwnerPermission
# from api.permissions
from api.authentication import TokenAuthentication
from .models import Product
from .serializers import ProductSerializer
from api.mixins import StaffEditorPermissionMixin


#
# class ProductListRetrieveAPIView(ListAPIView):
#
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

# class ProductMixinView(
#     ListModelMixin,
#     GenericAPIView,
#     RetrieveModelMixin,
#     CreateModelMixin,
#     DestroyModelMixin,
#     UpdateModelMixin,
#
# ):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     lookup_field = 'pk'
#     def get(self, request, *args, **kwargs):
#         pk = self.kwargs.get('pk', None)
#         if pk is not None:
#             return self.retrieve(request, *args, **kwargs)
#
#         return self.list(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)
#
#     def put(self, request, *args, **kwargs):
#         return self.update(request, *args, **kwargs)
#
#     def delete(self, request, *args, **kwargs):
#         return self.destroy(request, *args, **kwargs)
#
#     def perform_update(self, serializer):
#         content = serializer.validated_data.get('content', None)
#         if content is None:
#             content = 'Updated product content'
#         serializer.save(content=content)
#
#
#     def perform_create(self, serializer):
#         title = serializer.validated_data.get('title')
#         content = serializer.validated_data.get('content', None)
#         if content is None:
#             content = title
#         serializer.save(content=content)


class ProductListCreateAPIView(
    # StaffEditorPermissionMixin,
    # UserQuerySetMixin,
    ListCreateAPIView
):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [authentication.SessionAuthentication, TokenAuthentication]
    allow_staff_view = False
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        # email = serializer.validated_data.pop('email')
        # print(email)

        title = serializer.validated_data.get('title')
        content = serializer.validated_data.get('content', 'blank')
        serializer.save(content=content, user=self.request.user)


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
