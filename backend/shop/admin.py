from django.contrib import admin

from .models import Permission, ProductUpload, Shop, ShopManager, ShopStaffGroup

admin.site.register(ShopManager)
admin.site.register(ShopStaffGroup)
admin.site.register(Permission)
admin.site.register(ProductUpload)


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'slug', 'active')
# Register your models here.
