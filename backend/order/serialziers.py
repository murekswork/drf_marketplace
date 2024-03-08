from api.serializers import UserSerializer
from products.models import Product
from rest_framework import serializers
from rest_framework.reverse import reverse

from .models import Order
from .validators import positive_integer_validator


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = serializers.SerializerMethodField(read_only=True)
    product_pk = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True)
    amount = serializers.SerializerMethodField()
    count = serializers.IntegerField(validators=[positive_integer_validator])
    payment_status = serializers.BooleanField(read_only=True)
    payment_url = serializers.SerializerMethodField()
    lifetime = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def get_payment_url(self, object):
        if object.payment_status is True:
            return ''
        return reverse('order-payment', kwargs={'pk': object.pk}, request=self.context.get('request'))

    def get_product(self, object):
        request = self.context.get('request')
        return reverse(
            viewname='product-detail', request=request, kwargs={'pk': object.product.pk}
        )

    def get_amount(self, object):
        sale = object.product.sales.all()
        if sale and object.payment_status is not True:
            return str(
                (float(object.product.price) - (float(object.product.price) * 0.01 * float(sale[0].size))) * object.count)
        return object.amount

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        product_pk = validated_data.pop('product_pk')
        product = Product.objects.get(pk=product_pk.pk)
        count = validated_data.pop('count')
        amount = product.price * count
        order = Order.objects.create(product=product, user=user, amount=amount, count=count)
        return order
