import time

from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from api.authentication import TokenAuthentication
from rest_framework.generics import RetrieveAPIView, ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.mixins import UserQuerySetMixin
from shop.models import Shop, ProductUpload
from shop.permissions import IsShopOwner
from shop.serializers import ShopSerializer, ProductUploadSerializer
from shop.throttles import OncePerHourThrottleForPost
from shop.services.service import ProductCSVUploader
from celery_app import get_upload_logs


class ShopDetailAPIView(RetrieveAPIView):
    serializer_class = ShopSerializer
    queryset = Shop.objects.all()


class ShopListAPIView(ListAPIView):
    serializer_class = ShopSerializer
    queryset = Shop.objects.all()


class UploadCSVProductsAPIView(
    UserQuerySetMixin,
    APIView,
):
    permission_classes = [IsShopOwner]
    serializer_class = ProductUploadSerializer
    queryset = ProductUpload.objects.all()
    authentication_classes = (TokenAuthentication, SessionAuthentication,)
    throttle_classes = (OncePerHourThrottleForPost,)

    def post(self, request, format=None):
        self.check_permissions(request)
        file = request.data.get('file', None)
        if file is not None:
            upload = ProductUpload.objects.create(user=self.request.user,
                                                  file_name=f'{time.time()}_{self.request.user}')
            upload.save()
            service = ProductCSVUploader(source=file, user=self.request.user)
            service.upload()
            tasks = service.get_tasks()
            get_upload_logs.delay(tasks=tasks, upload_id=str(upload.id))
            msg = 'Started to uploading provided csv file'
        else:
            msg = 'No file provided'
        return Response({'message': msg})

    def get(self, request, pk: int):
        obj = get_object_or_404(ProductUpload, pk=pk)
        try:
            with open(f'backend/tasks_data/{obj.file_name}.txt', mode='r') as f:
                logs = f.read()
                return Response(logs, status=200)
        except Exception as e:
            return Response(f'Your products are not uploaded yet! {e}', status=status.HTTP_425_TOO_EARLY)


class UploadsAPIVIew(
    UserQuerySetMixin,
    ListAPIView
):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProductUploadSerializer
    queryset = ProductUpload.objects.all()
    authentication_classes = (TokenAuthentication, SessionAuthentication,)

# Create your views here.
