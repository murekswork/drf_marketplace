import time

from api.authentication import TokenAuthentication
from api.mixins import UserQuerySetMixin
from celery_app import create_product_upload_report
from django.http import FileResponse
from rest_framework import serializers, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from shop.models import ProductUpload, Shop
from shop.permissions import IsShopOwner
from shop.serializers import (
    ProductUploadSerializer,
    ShopSerializer,
    ShopWithProductsSerializer,
)
from shop.services.service import ProductCSVUploader
from shop.throttles import OncePerHourThrottleForPost


class ShopDetailAPIView(RetrieveAPIView):
    serializer_class = ShopWithProductsSerializer
    queryset = Shop.objects.all().prefetch_related('shopmanager_set', 'shopmanager_set__group',
                                                   'shopmanager_set__user', 'products', 'products__sales')
    lookup_field = 'slug'


class ShopListAPIView(ListAPIView):
    serializer_class = ShopSerializer
    queryset = Shop.objects.all().prefetch_related('shopmanager_set', 'shopmanager_set__group', 'shopmanager_set__user')


class UploadCSVProductsAPIView(
    UserQuerySetMixin,
    APIView,
):
    permission_classes = [IsShopOwner]
    serializer_class = ProductUploadSerializer
    queryset = ProductUpload.objects.all()
    authentication_classes = (TokenAuthentication, SessionAuthentication,)
    throttle_classes = (OncePerHourThrottleForPost,)

    def post(self, request, slug: str, format=None):
        shop = get_object_or_404(Shop, slug=slug)
        if shop.user != request.user:
            return Response('Its not your shop!', status=status.HTTP_403_FORBIDDEN)

        self.check_permissions(request)
        file = request.data.get('file', None)

        # TODO: delegate ProductCSVUploader service actions to celery !
        if file is not None:
            upload = ProductUpload.objects.create(user=self.request.user,
                                                  file_name=f'{time.time()}_{self.request.user}')
            upload.save()
            service = ProductCSVUploader(source=file, shop=shop)
            service.upload()
            service.save_tasks()
            tasks_filename = service.get_tasks_filename()
            create_product_upload_report.delay(tasks_file_name=tasks_filename, upload_id=str(upload.id))
            msg = 'Started to uploading provided csv file'
        else:
            msg = 'No file provided'
        return Response({'message': msg})

    def get(self, request, slug: str, pk: int):
        shop = get_object_or_404(Shop, slug=slug)
        if shop.user != request.user:
            return Response('Its not your shop!', status=status.HTTP_403_FORBIDDEN)
        obj = get_object_or_404(ProductUpload, pk=pk)
        file = f'backend/tasks_data/{obj.file_name}.csv'
        try:
            response = FileResponse(open(file, mode='rb'), as_attachment=True, filename='upload_results.csv')
            return response
        except Exception as e:
            return Response(f'Your products are not uploaded yet! {e}', status=status.HTTP_425_TOO_EARLY)


class UploadsAPIVIew(
    UserQuerySetMixin,
    APIView
):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProductUploadSerializer
    queryset = ProductUpload.objects.all()
    authentication_classes = (TokenAuthentication, SessionAuthentication,)

    # TODO: rewrite UploadProduct model with shop as user field and then filter by shop slug ( OR ID!!! )
    def get(self, request, slug, *args, **kwargs):
        queryset = ProductUpload.objects.filter(user=request.user)
        serializer = self.serializer_class(queryset, many=True, context={'request': request, 'slug': slug})
        return Response(serializer.data)
