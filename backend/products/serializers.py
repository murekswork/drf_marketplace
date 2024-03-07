from api.serializers import UserSerializer
from articles.serializers import ArticleInlineSerializer
from products.models import Product
from rest_framework import serializers, validators
from rest_framework.reverse import reverse

from .validators import english_words_validator
from celery_app import check_badwords_product


product_title_content_validator = validators.UniqueTogetherValidator(
    queryset=Product.objects.all(),
    fields=('title', 'content'),
    message='Fields title and content must be unique together for Products!'
)


class SaleInlineSerializer(serializers.Serializer):
    size = serializers.DecimalField(max_digits=4, decimal_places=2)


class ProductInlineSerializer(serializers.Serializer):
    title = serializers.CharField(read_only=True)
    url = serializers.SerializerMethodField()
    price = serializers.DecimalField(read_only=True, max_digits=15, decimal_places=2)
    owner = serializers.CharField(source='user.username', read_only=True)

    def get_url(self, obj):
        request = self.context.get('request', None)
        if request is None:
            return None
        return reverse('product-detail', kwargs={'pk': obj.id}, request=request)


class ProductSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='product-detail', lookup_field='pk', read_only=True)
    sales_count = serializers.IntegerField(read_only=True)
    sale = serializers.SerializerMethodField(read_only=True)
    sale_price = serializers.SerializerMethodField(read_only=True)
    owner = serializers.CharField(source='user.username', read_only=True)
    mark = serializers.DecimalField(max_digits=4, decimal_places=2, read_only=True)

    def create(self, validated_data):
        user = self.context.get('request').user
        if not user:
            raise serializers.ValidationError('User is not authenticated')
        obj = super().create(validated_data)
        check_badwords_product.delay(obj.id)
        return obj

    def get_sale(self, obj):
        if obj.sales.exists():
            return obj.sales.all()[0].size
        return None

    def get_sale_price(self, obj):
        sale = self.get_sale(obj)
        if sale:
            return obj.price - (obj.price * sale / 100)
        return None

    class Meta:
        model = Product
        fields = ('title', 'content', 'price', 'sale', 'sales_count', 'sale_price', 'url', 'owner', 'mark')


class ProductSerializerFull(ProductSerializer):
    edit_url = serializers.SerializerMethodField(read_only=True)
    title = serializers.CharField(
        validators=[english_words_validator],
        max_length=120,
        required=True)
    owner = UserSerializer(source='user', read_only=True)
    # mark = serializers.SerializerMethodField(read_only=True)
    # categories = serializers.ListField(source='category')
    category = serializers.SerializerMethodField(read_only=True)
    # similar_products = serializers.SerializerMethodField()
    reviews = ArticleInlineSerializer(source='articles', many=True, read_only=True)


    def get_category(self, obj):
        category = obj.category.all()
        if category:
            return list(cat.title for cat in category)
        else:
            return []


    # def get_similar_products(self, obj):
    #     qs = Product.objects.search(obj.title).exclude(id=obj.id)
    #     return ProductInlineSerializer(qs, many=True, context=self.context).data

    # def get_reviews(self, obj):
    #     return ArticleInlineSerializer(obj.articles.all(), many=True).data

    # def get_reviews(self, obj):
    #     return ArticleInlineSerializer(obj.articles.filter(published=True), many=True).data

    # def get_categories(self, obj):
    #     categories = obj.category.prefetch_related()
    #     if categories:
    #         return [category.title for category in categories]
    #     return []

    class Meta:
        model = Product
        fields = ('title', 'content', 'price', 'sale', 'sales_count', 'sale_price', 'url',
                  'reviews', 'category', 'edit_url', 'mark')
        validators = [
            product_title_content_validator
        ]

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.price = validated_data.get('price', instance.price)
        return instance

    def get_edit_url(self, obj):
        request = self.context.get('request', None)
        if request is None:
            return None
        return reverse(
            'product-update', kwargs={'pk': obj.pk}, request=request
        )
