from rest_framework import serializers
from .models import Module, Action, Permission, Role, UserRole


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ['id', 'name', 'code', 'description']


class ModuleSerializer(serializers.ModelSerializer):
    actions = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ['id', 'name', 'code', 'description', 'actions']

    def get_actions(self, obj):
        """Get all actions available for this module based on user's permissions"""
        user = self.context.get('user')
        if not user:
            return []
        
        user_permissions = Permission.objects.filter(
            roles__user_roles__user=user,
            module=obj,
            is_active=True
        ).select_related('action')
        
        actions = [perm.action for perm in user_permissions if perm.action.is_active]
        return ActionSerializer(actions, many=True).data


class PermissionSerializer(serializers.ModelSerializer):
    module = ModuleSerializer(read_only=True)
    action = ActionSerializer(read_only=True)

    class Meta:
        model = Permission
        fields = ['id', 'name', 'code', 'module', 'action']


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'code', 'description', 'permissions']


class UserAccessSerializer(serializers.Serializer):
    """Serializer for user's accessible modules and actions"""
    modules = ModuleSerializer(many=True, read_only=True)
    roles = serializers.SerializerMethodField()

    def get_roles(self, obj):
        return [role.name for role in obj.get('roles', [])]


class UserRoleSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    assigned_by_email = serializers.CharField(source='assigned_by.email', read_only=True)

    class Meta:
        model = UserRole
        fields = ['id', 'user', 'user_email', 'role', 'assigned_at', 'assigned_by', 'assigned_by_email']
