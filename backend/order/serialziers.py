from api.serializers import UserSerializer
from products.models import Product
from products.serializers import ProductInlineSerializer
from rest_framework import serializers
from rest_framework.reverse import reverse

from .models import Order
from .validators import positive_integer_validator


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    choose_product = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Product.objects.filter(public=True))
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

    def get_amount(self, obj):
        sale = obj.product.sales.all()
        if sale and obj.payment_status is not True:
            return (float(obj.product.price) - (float(obj.product.price) * 0.01 * float(sale[0].size))) * obj.count
        return obj.amount

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        product_pk = validated_data.pop('choose_product')
        product = Product.objects.get(pk=product_pk.pk)
        count = validated_data.pop('count')
        amount = product.price * count
        order = Order.objects.create(product=product, user=user, amount=amount, count=count)
        return order
