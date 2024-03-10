from rest_framework.permissions import IsAuthenticated


class IsShopOwner(IsAuthenticated):

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.shop_owned


class ProductShopStaffPermission(IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        action = None
        if request.method in ('PUT', 'PATCH'):
            action = 'update'
        elif request.method in ('DELETE',):
            action = 'delete'
        shop = obj.shop
        user_role = shop.managers.through.objects.filter(user=request.user)
        if user_role.exists():
            user_role = user_role.all()[0]
            if user_role.has_permission(f'{action}_shop_product'):
                return True
        return False
