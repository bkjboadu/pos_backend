from django.db import models
from users.models import CustomUser


class Module(models.Model):
    """Represents application modules like Dashboard, Staff Management, etc."""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)  # e.g., 'dashboard', 'staff_management'
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'rbac_modules'
        ordering = ['name']


class Action(models.Model):
    """Represents actions that can be performed on modules"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)  # e.g., 'create', 'edit', 'delete', 'view'
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'rbac_actions'
        ordering = ['name']


class Permission(models.Model):
    """Represents a permission (module + action combination)"""
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='permissions')
    action = models.ForeignKey(Action, on_delete=models.CASCADE, related_name='permissions')
    name = models.CharField(max_length=200)  # e.g., 'Dashboard View', 'Staff Create'
    code = models.CharField(max_length=100, unique=True)  # e.g., 'dashboard_view', 'staff_create'
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'rbac_permissions'
        unique_together = ('module', 'action')
        ordering = ['module__name', 'action__name']


class Role(models.Model):
    """Represents user roles with associated permissions"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, related_name='roles', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'rbac_roles'
        ordering = ['name']


class UserRole(models.Model):
    """Associates users with roles"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles')
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_roles'
    )

    def __str__(self):
        return f"{self.user.email} - {self.role.name}"

    class Meta:
        db_table = 'rbac_user_roles'
        unique_together = ('user', 'role')
        ordering = ['user__email', 'role__name']
