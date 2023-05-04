from rest_framework import permissions


class isParent(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if obj.users.filter(id=request.user.id).exists():
            return True
        return False
