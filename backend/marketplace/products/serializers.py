from articles.serializers import ArticleInlineSerializer
from celery_app import check_badwords_product
from django.db.models import Q
from products.models import Product
from rest_framework import serializers, validators
from rest_framework.reverse import reverse
from shop.models import Shop, ShopPermissions

from .validators import english_words_validator

product_title_content_validator = validators.UniqueTogetherValidator(
    queryset=Product.objects.all(),
    fields=("title", "content"),
    message="Fields title and content must be unique together for Products!",
)


class SaleInlineSerializer(serializers.Serializer):
    size = serializers.DecimalField(max_digits=4, decimal_places=2)


class ProductInlineSerializer(serializers.Serializer):
    title = serializers.CharField(read_only=True)
    url = serializers.SerializerMethodField()
    price = serializers.DecimalField(read_only=True, max_digits=15, decimal_places=2)
    shop = serializers.CharField(source="shop.title", read_only=True)

    def get_url(self, obj):
        request = self.context.get("request", None)
        if request is None:
            return None
        return reverse("product-detail", kwargs={"pk": obj.id}, request=request)


class ProductSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="product-detail", lookup_field="pk", read_only=True
    )
    sales_count = serializers.IntegerField(read_only=True)
    sale = serializers.SerializerMethodField(read_only=True)
    sale_price = serializers.SerializerMethodField(read_only=True)
    seller = serializers.SerializerMethodField(read_only=True)
    shop = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Shop.objects.none()
    )
    mark = serializers.DecimalField(max_digits=4, decimal_places=2, read_only=True)

    def get_seller(self, obj):
        return reverse(
            "shop-detail",
            kwargs={"slug": obj.shop.slug},
            request=self.context.get("request"),
        )

    def get_fields(self):
        fields = super().get_fields()
        if self.context.get("request", None) is not None:
            user = self.context.get("request").user
            if user.is_authenticated:
                shops = Shop.objects.filter(
                    Q(user=user)
                    | Q(
                        shopmanager__user=user,
                        shopmanager__group__permissions=ShopPermissions.CREATE_PRODUCT,
                    )
                ).distinct()
                fields["shop"].queryset = shops

        return fields

    def create(self, validated_data):
        user = self.context.get("request").user
        if not user:
            raise serializers.ValidationError("User is not authenticated")
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
        fields = (
            "title",
            "content",
            "price",
            "seller",
            "quantity",
            "sale",
            "sales_count",
            "sale_price",
            "url",
            "shop",
            "mark",
        )


class ProductCreateSerializer(ProductSerializer):
    shop_id = serializers.PrimaryKeyRelatedField(
        queryset=Shop.objects.all(), write_only=True
    )

    class Meta:
        model = Product
        fields = (
            "title",
            "content",
            "price",
            "seller",
            "sale",
            "sales_count",
            "sale_price",
            "url",
            "shop_id",
            "mark",
        )


class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("title", "content", "price", "quantity")

    def update(self, instance, validated_data):
        user = self.context.get("request").user
        if not user:
            raise serializers.ValidationError("User is not authenticated")
        obj = super().update(instance, validated_data)
        check_badwords_product.delay(obj.id)
        return obj


class ProductSerializerFull(ProductSerializer):
    edit_url = serializers.SerializerMethodField(read_only=True)
    title = serializers.CharField(
        validators=[english_words_validator], max_length=120, required=True
    )
    category = serializers.SerializerMethodField(read_only=True)
    reviews = ArticleInlineSerializer(source="articles", many=True, read_only=True)

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
        fields = (
            "title",
            "content",
            "price",
            "sale",
            "sales_count",
            "sale_price",
            "url",
            "reviews",
            "category",
            "edit_url",
            "mark",
            "seller",
            "shop",
        )
        validators = [product_title_content_validator]

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.content = validated_data.get("content", instance.content)
        instance.price = validated_data.get("price", instance.price)
        return instance

    def get_edit_url(self, obj):
        request = self.context.get("request", None)
        if request is None:
            return None
        return reverse("product-update", kwargs={"pk": obj.pk}, request=request)
