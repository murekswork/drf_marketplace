from rest_framework import permissions

from .permissions import IsStaffEditorPermission


class IsObjectOwnerPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        print(f'CHECK OWNERSHIP PERM AND ITS {obj.user} and {request.user}')
        return obj.user == request.user


class StaffEditorPermissionMixin:

    permission_classes = [IsObjectOwnerPermission, permissions.IsAdminUser, IsStaffEditorPermission]


class UserQuerySetMixin:

    user_field = 'user'
    allow_staff_view = False
    allow_superuser_view = True

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if self.allow_staff_view is True and user.is_superuser:
            return qs

        if self.allow_staff_view and user.is_staff:
            return qs

        lookup_data = {}
        lookup_data[self.user_field] = user
        return qs.filter(**lookup_data)
