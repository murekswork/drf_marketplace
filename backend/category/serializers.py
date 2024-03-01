from rest_framework import serializers
from rest_framework.reverse import reverse


from .models import Category


class CategorySerializer(serializers.ModelSerializer):

    category_url = serializers.SerializerMethodField()

    def get_category_url(self, obj):
        return reverse('category-detail', kwargs={'slug': obj.slug}, request=self.context.get('request'))

    class Meta:
        model = Category
        fields = '__all__'