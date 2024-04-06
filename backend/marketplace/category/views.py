from products.models import Product
from products.serializers import ProductSerializer
from rest_framework.generics import ListAPIView

from .models import Category
from .serializers import CategorySerializer


class CategoryDetailView(ListAPIView):

    lookup_field = "slug"
    serializer_class = ProductSerializer

    # def get(self, request, *args, **kwargs):
    #     products = self.get_queryset()
    #     # serializer = ProductSerializer(products, many=True, context={'request': request})
    #     return Response(serializer.data)

    def get_object(self):
        return Category.objects.filter(slug=self.kwargs["slug"]).first()

    def get_queryset(self):
        return Product.objects.filter(category=self.get_object())


class CategoryListAPIView(ListAPIView):

    serializer_class = CategorySerializer
    queryset = Category.objects.all()
