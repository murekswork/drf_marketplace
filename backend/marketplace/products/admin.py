from django.contrib import admin
from products.models import Product, Sale


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = ("id", "title", "content", "price")


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):

    list_display = ("id", "size", "end_date")


# Register your models here.
