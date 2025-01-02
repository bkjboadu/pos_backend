from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    """
    Allow access only to superusers.
    """

    def has_permission(self, request, view):
        return request.user.is_superuser


class IsSuperUserOrCompanyAdmin(BasePermission):
    """
    Allow access to superusers or company admins.
    Company admins can only access resources related to their company.
    """

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return request.user.role == "company_admin" and request.user.company is not None

    def has_object_permission(self, request, view, obj):
        # Superusers can access all objects
        if request.user.is_superuser:
            return True

        # Company admins can access objects only if they belong to their company
        if request.user.role == "company_admin" and request.user.company is not None:
            return obj.company == request.user.company
        return False


class IsSuperUserOrCompanyAdminOrBranchManager(BasePermission):
    """
    Allow access to superusers or company admins or branch manager.
    Company admins can only access resources related to their company.
    """

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.user.role == "company_admin" and request.user.company is not None:
            return True
        if request.user.role == "branch_manager" and request.user.company is not None:
            return True

    def has_object_permission(self, request, view, obj):
        # Superusers can access all objects
        if request.user.is_superuser:
            return True

        # Company admins can access objects only if they belong to their company
        if request.user.role == "company_admin" and request.user.company is not None:
            return obj.company == request.user.company

        if request.user.role == "branch_manager" and request.user.company is not None:
            return obj.branch == request.user.branch
        return False
