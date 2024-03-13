from api.serializers import UserSerializer
from products.models import Product
from products.serializers import ProductInlineSerializer
from rest_framework import serializers
from rest_framework.reverse import reverse

from .models import Order
from .services.order_service import OrderAmountCalculator
from .validators import positive_integer_validator


class OrderCreateSerializer(OrderAmountCalculator, serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    shop = serializers.CharField(source='product.shop', read_only=True)
    count = serializers.IntegerField(validators=[positive_integer_validator])
    amount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = ('product', 'count', 'shop', 'amount', 'id')

    def create(self, validated_data):
        user = self.context.get('request').user
        if validated_data['product'].shop.user == user:
            raise serializers.ValidationError('Invalid product!')

        validated_data['user'] = user
        validated_data['amount'] = self._create_amount(product=validated_data['product'], count=validated_data['count'])
        return super().create(validated_data)


class OrderSerializer(serializers.ModelSerializer, OrderAmountCalculator):
    user = UserSerializer(read_only=True)
    product = ProductInlineSerializer(read_only=True)
    amount = serializers.SerializerMethodField()
    count = serializers.IntegerField(validators=[positive_integer_validator])
    payment_status = serializers.BooleanField(read_only=True)
    payment_url = serializers.SerializerMethodField()
    lifetime = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def get_payment_url(self, obj):
        if obj.payment_status is True:
            return ''
        return reverse('order-payment', kwargs={'pk': obj.pk}, request=self.context.get('request'))

    def get_product_url(self, obj):
        request = self.context.get('request')
        return reverse(
            viewname='product-detail', request=request, kwargs={'pk': obj.product.pk}
        )

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        product_pk = validated_data.pop('choose_product')
        product = Product.objects.get(pk=product_pk.pk)
        count = validated_data.pop('count')
        amount = product.price * count
        order = Order.objects.create(product=product, user=user, amount=amount, count=count)
        return order
