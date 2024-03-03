from api.serializers import UserSerializer
from articles.serializers import ArticleInlineSerializer
from category.models import Category
from products.models import Product
from rest_framework import serializers, validators
from rest_framework.reverse import reverse

from .validators import english_words_validator

product_title_content_validator = validators.UniqueTogetherValidator(
    queryset=Product.objects.all(),
    fields=('title', 'content'),
    message='Fields title and content must be unique together for Products!'
)


class ProductInlineSerializer(serializers.Serializer):
    title = serializers.CharField(read_only=True)
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        request = self.context.get('request', None)
        if request is None:
            return None
        return reverse('product-detail', kwargs={'pk': obj.id}, request=request)


class ProductSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='product-detail', read_only=True, lookup_field='pk')
    edit_url = serializers.SerializerMethodField(read_only=True)
    title = serializers.CharField(
        validators=[english_words_validator],
        max_length=120,
        required=True)
    owner = UserSerializer(source='user', read_only=True)
    reviews = ArticleInlineSerializer(many=True, read_only=True, source='article_set')
    mark = serializers.SerializerMethodField(read_only=True)
    categories = serializers.SerializerMethodField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Category.objects.all(), many=True)
    sale_price = serializers.SerializerMethodField(read_only=True)

    def get_sale_price(self, obj):
        obj_sale = obj.sale.select_related()
        if obj_sale.exists():
            return str(float(obj.price) - (float(obj.price) * 0.01 * float(obj_sale.first().size)))
        return 'Not sale'

    def get_categories(self, obj):
        categories = obj.category.prefetch_related()
        if categories is not None:
            return [category.title for category in categories]
        return 'No Category'

    class Meta:
        model = Product
        fields = (
            'url',
            'owner',
            'edit_url',
            'title',
            'content',
            'price',
            'quantity',
            'sale_price',
            'public',
            'reviews',
            'mark',
            'categories',
            'category',

        )
        validators = [
            product_title_content_validator
        ]

    def get_mark(self, product):
        articles = product.article_set.select_related()
        mark = 5
        if articles:
            mark = (sum(article.mark for article in articles) / len(articles))
        return mark

    def create(self, validated_data):
        user = self.context.get('request').user
        if not user:
            raise serializers.ValidationError('User is not authenticated')

        obj = super().create(validated_data)
        return obj

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
