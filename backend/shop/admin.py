from django.contrib import admin

from .models import Permission, ProductUpload, Shop, ShopManager, ShopStaffGroup

admin.site.register(Shop)
admin.site.register(ShopManager)
admin.site.register(ShopStaffGroup)
admin.site.register(Permission)
admin.site.register(ProductUpload)

# Register your models here.
