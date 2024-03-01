import re

from rest_framework import serializers, validators

from .models import Product

product_title_validator = validators.UniqueValidator(queryset=Product.objects.all(), lookup='iexact')


def title_validator(value):

    qs = Product.objects.filter(title__iexact=value)
    if qs.exists():
        raise serializers.ValidationError(f'Product with name {value} already exists!')
    return value


def english_words_validator(value):
    english_letters_pattern = r'^[A-Za-z0-9]+$'
    if not re.match(english_letters_pattern, value):
        raise serializers.ValidationError('Use only english letters or digits!')
    return value
