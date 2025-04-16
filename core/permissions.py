from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    """
    Allow access only to superusers.
    """

    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.role == "admin_manager"


class IsSuperUserOrManager(BasePermission):
    """
    Allow access to superusers or company admins.
    Company admins can only access resources related to their company.
    """

    def has_permission(self, request, view):
        if request.user.is_superuser :
            return True
        if request.user.role == "admin_manager":
            return True
        return request.user.role == "manager"

    def has_object_permission(self, request, view, obj):
        # Superusers can access all objects
        if request.user.is_superuser:
            return True

        if request.user.role == "admin_manager":
            return True

        # @TODO:admins can access objects only if they belong to that branch
        if request.user.role == "manager":
            True
        return False
