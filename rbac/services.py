from django.db.models import Q
from .models import Module, Action, Permission, Role, UserRole
from users.models import CustomUser


class RBACService:
    """Service class to handle RBAC operations"""

    @staticmethod
    def get_user_modules_and_actions(user):
        """Get all modules and actions accessible by a user"""
        if not user.is_authenticated:
            return []

        # Get user's roles
        user_roles = Role.objects.filter(
            user_roles__user=user,
            is_active=True
        ).prefetch_related('permissions__module', 'permissions__action')

        # Get all modules the user has access to
        modules = Module.objects.filter(
            permissions__roles__in=user_roles,
            is_active=True
        ).distinct().order_by('name')

        return modules

    @staticmethod
    def get_user_permissions(user):
        """Get all permissions for a user"""
        if not user.is_authenticated:
            return Permission.objects.none()

        return Permission.objects.filter(
            roles__user_roles__user=user,
            is_active=True
        ).select_related('module', 'action').distinct()

    @staticmethod
    def user_has_permission(user, module_code, action_code):
        """Check if user has a specific permission"""
        if not user.is_authenticated:
            return False

        # Superusers have all permissions
        if user.is_superuser:
            return True

        return Permission.objects.filter(
            roles__user_roles__user=user,
            module__code=module_code,
            action__code=action_code,
            is_active=True
        ).exists()

    @staticmethod
    def assign_role_to_user(user, role, assigned_by=None):
        """Assign a role to a user"""
        user_role, created = UserRole.objects.get_or_create(
            user=user,
            role=role,
            defaults={'assigned_by': assigned_by}
        )
        return user_role, created

    @staticmethod
    def remove_role_from_user(user, role):
        """Remove a role from a user"""
        return UserRole.objects.filter(user=user, role=role).delete()

    @staticmethod
    def get_user_roles(user):
        """Get all roles assigned to a user"""
        return Role.objects.filter(user_roles__user=user, is_active=True)

    @staticmethod
    def sync_user_role_with_legacy_role(user):
        """Sync user's RBAC role with their legacy role field"""
        # Remove existing RBAC roles
        UserRole.objects.filter(user=user).delete()
        
        # Assign RBAC role based on legacy role
        if user.role:
            try:
                rbac_role = Role.objects.get(code=user.role)
                RBACService.assign_role_to_user(user, rbac_role)
            except Role.DoesNotExist:
                pass  # Role doesn't exist in RBAC system yet
