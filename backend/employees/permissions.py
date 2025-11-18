from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsManager(BasePermission):
    """Allow access only to users with role MANAGER for unsafe methods.

    Read-only (safe) methods are allowed to authenticated users.
    """

    def has_permission(self, request, view):  # type: ignore[override]
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return getattr(request.user, 'role', None) == 'MANAGER' or request.user.is_superuser
