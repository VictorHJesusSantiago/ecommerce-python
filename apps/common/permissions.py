from rest_framework import permissions
from django.contrib.auth.models import Group


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return obj == request.user


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser


class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            not request.user.is_staff
        )


class IsVendor(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'vendor_profile') and
            request.user.vendor_profile.is_approved
        )


class IsOrderOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.user == request.user


class IsReviewOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsProductOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if hasattr(obj, 'vendor'):
            return obj.vendor.user == request.user
        return False


class HasRolePermission(permissions.BasePermission):
    required_roles = []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        user_roles = set(request.user.groups.values_list('name', flat=True))
        return bool(user_roles.intersection(self.required_roles))


class CanManageProducts(HasRolePermission):
    required_roles = ['product_manager', 'admin']


class CanManageOrders(HasRolePermission):
    required_roles = ['order_manager', 'admin', 'customer_support']


class CanManageInventory(HasRolePermission):
    required_roles = ['inventory_manager', 'admin']


class CanManageMarketing(HasRolePermission):
    required_roles = ['marketing_manager', 'admin']


class CanManageReports(HasRolePermission):
    required_roles = ['analyst', 'admin']


class CanManageCMS(HasRolePermission):
    required_roles = ['content_manager', 'admin']


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class AllowAnyAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsAuthenticatedOrWriteOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return request.user and request.user.is_authenticated
