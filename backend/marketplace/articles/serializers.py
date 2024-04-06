from celery_app import check_badwords_article
from order.models import Order
from products.models import Product
from rest_framework import serializers
from rest_framework.reverse import reverse

from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        lookup_field="pk", read_only=True, view_name="article-detail"
    )
    product = serializers.SerializerMethodField()
    order = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.none(), write_only=True
    )

    class Meta:
        model = Article
        fields = [
            "title",
            "url",
            "article_content",
            "created_at",
            "mark",
            "product",
            "order",
        ]

    def get_product(self, obj):
        return reverse(
            "product-detail",
            kwargs={"pk": obj.product.pk},
            request=self.context.get("request"),
        )

    def create(self, validated_data):
        order = validated_data.pop("review_order")
        validated_data["product"] = Product.objects.get(pk=order.product.pk)
        validated_data["order"] = order
        validated_data["user"] = self.context["request"].user
        obj = super().create(validated_data)

        check_badwords_article.delay(obj.id)

        return obj

    def get_fields(self):
        fields = super().get_fields()
        fields["order"].queryset = Order.objects.get_not_reviewed_orders(
            self.context.get("request").user
        )
        return fields


class ArticleInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            "user",
            "title",
            "content",
            "mark",
            "created_at",
        ]
