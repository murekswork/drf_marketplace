import logging

from rest_framework.reverse import reverse

from order.models import Order
from products.models import Product
from rest_framework import serializers

from .models import Article
from articles.services.service import ArticleBadWordsValidator
from celery_app import check_badwords_article


class ArticleSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(lookup_field='pk', read_only=True, view_name='article-detail')
    product = serializers.SerializerMethodField()
    review_order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.none(), write_only=True)
    # order = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:

        model = Article
        fields = [
            'title',
            'url',
            'article_content',
            'created_at',
            'mark',
            'product',
            # 'order',
            'review_order',
        ]

    def get_product(self, obj):
        return reverse('product-detail', kwargs={'pk': obj.product.pk}, request=self.context.get('request'))

    def create(self, validated_data):
        order = validated_data.pop('review_order')
        validated_data['product'] = Product.objects.get(pk=order.product.pk)
        validated_data['order'] = order
        validated_data['user'] = self.context['request'].user
        obj = super().create(validated_data)
        logging.warning(
            'Created obj of article !!'
        )
        print(obj.__dict__)
        logging.warning(obj.__dict__)
        # create celery task for badwords validation
        check_badwords_article.delay(obj.id)

        return obj

    def get_fields(self):
        fields = super().get_fields()
        fields['review_order'].queryset = Order.objects.get_not_reviewed_orders(self.context.get('request').user)
        return fields

    def get_orders(self, obj):
        user = self.context.get('request').user
        orders = Order.objects.get_not_reviewed_orders(user=user)
        print(orders)
        return orders


class ArticleInlineSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = [
            'user',
            'title',
            'content',
            'mark',
            'created_at',
        ]
