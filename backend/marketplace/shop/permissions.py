from django.contrib.auth.models import Permission
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from shop.models import Shop, ShopPermissions


class IsShopOwner(IsAuthenticated):

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.shops_owned


class ShopStaffPermissionsMixin:

    def has_shop_permission(self, request, shop: Shop, permission: Permission | str):
        user = request.user
        if not user.is_authenticated:
            return False

        if user == shop.user:
            return True

        shop_manager = shop.managers.through.objects.filter(user=user)
        if shop_manager.exists():
            # in brackets expression checks each manager role for required permission, then all values are convert to
            # False by (NOT), so we can get hit if any check returned True because if there are False in set of True we
            # anyway get False, then we simply use second (NOT) to convert back found result
            return not all(
                not manager.has_permission(permission) for manager in shop_manager
            )

        return False


class ProductShopStaffPermission(permissions.BasePermission, ShopStaffPermissionsMixin):

    def has_object_permission(self, request, view, obj):
        if request.method in ('PUT', 'PATCH'):
            required_permission = ShopPermissions.UPDATE_PRODUCT
        elif request.method in ('DELETE',):
            required_permission = ShopPermissions.DELETE_PRODUCT
        else:
            return True
        shop = obj.shop
        return super().has_shop_permission(request, shop, required_permission)
