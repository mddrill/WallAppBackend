from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a thing to access it
    """
    def has_object_permission(self, request, view, obj):
        return obj == request.user

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow owners of something or admins to access that thing
    """
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff

class AllowNone(permissions.BasePermission):
    """
    Custom permission to allow no one to access something
    """
    def has_permission(self, request, view):
        return False
    def has_object_permission(self, request, view, obj):
        return False