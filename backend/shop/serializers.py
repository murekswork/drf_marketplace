from rest_framework import serializers
from rest_framework.reverse import reverse
from shop.models import ProductUpload, Shop, ShopManager


class ShopManagerSerializer(serializers.Serializer):
    username = serializers.PrimaryKeyRelatedField(source='user.username', read_only=True)
    group = serializers.CharField(max_length=120, read_only=True)


class ShopSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(lookup_field='slug', view_name='shop-detail', read_only=True)
    managers = serializers.SerializerMethodField(read_only=True)

    def get_managers(self, obj):
        qs = ShopManager.objects.filter(shop=obj)
        return ShopManagerSerializer(qs, many=True).data

    class Meta:
        model = Shop
        fields = ('title', 'description', 'url', 'managers')


# TODO: Add limit or pagination for products field
class ShopWithProductsSerializer(ShopSerializer):
    products = serializers.SerializerMethodField(read_only=True)

    def get_products(self, obj):
        from products.serializers import ProductSerializer
        qs = obj.products.filter(public=True)
        return ProductSerializer(qs, many=True, context=self.context).data

    class Meta:
        model = Shop
        fields = ('title', 'description', 'url', 'managers', 'products')


class ProductUploadSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(read_only=True)

    def get_url(self, obj):
        return reverse('upload-detail', kwargs={'pk': obj.pk}, request=self.context.get('request'))

    class Meta:
        model = ProductUpload
        fields = '__all__'


class ProductUploadDetailSerializer(serializers.Serializer):
    row_id = serializers.IntegerField(read_only=True)
    result = serializers.CharField(read_only=True, default=None)
    error = serializers.CharField(read_only=True, default=None)
