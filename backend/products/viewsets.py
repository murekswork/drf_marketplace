from rest_framework import viewsets

from .models import Product
from .serializers import ProductSerializer
from api.mixins import StaffEditorPermissionMixin

class ProductViewSet(StaffEditorPermissionMixin, viewsets.ModelViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer