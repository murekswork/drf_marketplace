from rest_framework.reverse import reverse
from rest_framework import serializers
from django.contrib.auth import get_user_model
from products.models import Product


class UserSerializer(serializers.Serializer):

    username = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
    # products = serializers.SerializerMethodField(read_only=True)
    #
    # def get_products(self, obj):
    #     products = obj.product_set.all()
    #     return UserProductsInlineSerializer(products, many=True, context=self.context).data