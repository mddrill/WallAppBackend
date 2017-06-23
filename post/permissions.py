from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow anyone to read something, but only owners to write to it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the author of the post.
        return obj.author == request.user

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to allows owners of a thing or admins to access that thing
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or request.user.is_staff