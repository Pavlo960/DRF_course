from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Read access for everyone, write access for staff only."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsOwnerOrStaff(permissions.BasePermission):
    """Object access only for the order owner or staff."""

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.owner == request.user


class IsEditableByCustomer(permissions.BasePermission):
    """Customers can change or delete an order only while it is still new."""

    message = 'Order is already being processed and can no longer be changed.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS or request.user.is_staff:
            return True
        return obj.status == obj.STATUS_NEW
