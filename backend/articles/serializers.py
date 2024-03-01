from rest_framework import serializers

from products.models import Product
from order.models import Order
from .models import Article


class ArticleSerializer(serializers.ModelSerializer):

    url = serializers.HyperlinkedIdentityField(lookup_field='pk', read_only=True, view_name='article-detail')
    product = serializers.HyperlinkedIdentityField(lookup_field='pk', view_name='product-detail')
    review_order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.none(), write_only=True)
    order = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:

        model = Article
        fields = [
            'title',
            'url',
            'article_content',
            'created_at',
            'mark',
            'product',
            'order',
            'review_order',
        ]

    def create(self, validated_data):
        order = validated_data.pop('review_order')
        validated_data['product'] = Product.objects.get(pk=order.product.pk)
        validated_data['order'] = order
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


    def get_fields(self):
        fields = super().get_fields()
        fields['review_order'].queryset = Order.objects.get_not_reviewed_orders(self.context.get('request').user)
        return fields


    def get_orders(self, obj):
        user = self.context.get('request').user
        orders =  Order.objects.get_not_reviewed_orders(user=user)
        print(orders)
        return orders

class ArticleInlineSerializer(serializers.ModelSerializer):

    user = serializers.PrimaryKeyRelatedField(source='user.username', read_only=True)

    class Meta:

        model = Article
        fields = [
            'user',
            'title',
            'content',
            'mark'
        ]
