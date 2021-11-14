from rest_framework import permissions

from reviews.models import UserRole


class OwnerAdminModeratorOrReadOnly(permissions.BasePermission):
    """Manage permissions.
    SAFE methods allowed for anyone.
    `POST` allowed for authenticated users.
    Other methods allowed for object author, moderator or admin.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            obj.author == request.user
            or request.user.role in [UserRole.MODERATOR, UserRole.ADMIN]
            or request.user.is_superuser)


class IsAdmin(permissions.IsAuthenticated):
    """Access for admin or superuser."""
    def has_permission(self, request, view):
        return super().has_permission(request, view) and (
            request.user.role == UserRole.ADMIN or request.user.is_superuser
        )


class IsAdminOrReadOnly(IsAdmin):
    """Manage permissions.
    SAFE methods allowed for anyone,
    inlcuding not authenticateed.
    `POST` allowed for admin.
    Other methods allowed for admin.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or super().has_permission(request, view))
