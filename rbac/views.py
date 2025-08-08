from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Module, Action, Permission, Role, UserRole
from .serializers import (
    ModuleSerializer, 
    ActionSerializer, 
    PermissionSerializer, 
    RoleSerializer,
    UserRoleSerializer
)
from .services import RBACService
from core.permissions import IsSuperUserOrManager


class UserAccessView(APIView):
    """Get user's accessible modules and actions"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Get user's accessible modules
        modules = RBACService.get_user_modules_and_actions(user)
        modules_data = ModuleSerializer(modules, many=True, context={'user': user}).data
        
        # Get user's roles
        user_roles = RBACService.get_user_roles(user)
        
        return Response({
            'modules': modules_data,
            'roles': [role.name for role in user_roles],
            'permissions': [perm.code for perm in RBACService.get_user_permissions(user)]
        })


class ModuleListView(APIView):
    """List all modules"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        modules = Module.objects.filter(is_active=True)
        serializer = ModuleSerializer(modules, many=True, context={'user': request.user})
        return Response(serializer.data)


class ActionListView(APIView):
    """List all actions"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        actions = Action.objects.filter(is_active=True)
        serializer = ActionSerializer(actions, many=True)
        return Response(serializer.data)


class RoleListView(APIView):
    """List all roles (admin only)"""
    permission_classes = [IsSuperUserOrManager]

    def get(self, request):
        roles = Role.objects.filter(is_active=True)
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)


class AssignRoleView(APIView):
    """Assign role to user (admin only)"""
    permission_classes = [IsSuperUserOrManager]

    def post(self, request):
        user_id = request.data.get('user_id')
        role_id = request.data.get('role_id')
        
        if not user_id or not role_id:
            return Response(
                {'error': 'user_id and role_id are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from users.models import CustomUser
            user = CustomUser.objects.get(id=user_id)
            role = Role.objects.get(id=role_id)
            
            user_role, created = RBACService.assign_role_to_user(
                user, role, assigned_by=request.user
            )
            
            if created:
                return Response({
                    'message': f'Role {role.name} assigned to {user.email}'
                })
            else:
                return Response({
                    'message': f'User {user.email} already has role {role.name}'
                })
                
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class RemoveRoleView(APIView):
    """Remove role from user (admin only)"""
    permission_classes = [IsSuperUserOrManager]

    def delete(self, request):
        user_id = request.data.get('user_id')
        role_id = request.data.get('role_id')
        
        if not user_id or not role_id:
            return Response(
                {'error': 'user_id and role_id are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from users.models import CustomUser
            user = CustomUser.objects.get(id=user_id)
            role = Role.objects.get(id=role_id)
            
            deleted_count, _ = RBACService.remove_role_from_user(user, role)
            
            if deleted_count > 0:
                return Response({
                    'message': f'Role {role.name} removed from {user.email}'
                })
            else:
                return Response({
                    'message': f'User {user.email} does not have role {role.name}'
                })
                
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_permission(request):
    """Check if user has specific permission"""
    module_code = request.GET.get('module')
    action_code = request.GET.get('action')
    
    if not module_code or not action_code:
        return Response(
            {'error': 'module and action parameters are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    has_permission = RBACService.user_has_permission(
        request.user, module_code, action_code
    )
    
    return Response({
        'has_permission': has_permission,
        'module': module_code,
        'action': action_code
    })


class UpdateRoleAccessView(APIView):
    """Update role's modules and permissions with actions (admin only)"""
    permission_classes = [IsSuperUserOrManager]

    def put(self, request):
        role_id = request.data.get('role_id')
        module_codes = request.data.get('modules', [])  # List of module codes for full access
        module_actions = request.data.get('module_actions', {})  # Dict: {module_code: [action_codes]}
        
        if not role_id:
            return Response(
                {'error': 'role_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            role = Role.objects.get(id=role_id)
            
            # Clear existing assignments
            role.modules.clear()
            role.permissions.clear()
            
            # Handle modules with full access
            if module_codes:
                if not isinstance(module_codes, list):
                    return Response(
                        {'error': 'modules must be a list of module codes'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                modules = Module.objects.filter(code__in=module_codes, is_active=True)
                
                # Check if all requested modules exist
                found_module_codes = set(modules.values_list('code', flat=True))
                requested_module_codes = set(module_codes)
                missing_module_codes = requested_module_codes - found_module_codes
                
                if missing_module_codes:
                    return Response(
                        {'error': f'Modules not found: {", ".join(missing_module_codes)}'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Assign modules for full access
                role.modules.set(modules)
                
                # Also assign all permissions for these modules
                all_permissions_for_modules = Permission.objects.filter(
                    module__in=modules,
                    is_active=True
                )
                role.permissions.add(*all_permissions_for_modules)
            
            # Handle module-specific actions
            if module_actions:
                if not isinstance(module_actions, dict):
                    return Response(
                        {'error': 'module_actions must be a dictionary of {module_code: [action_codes]}'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                for module_code, action_codes in module_actions.items():
                    if not isinstance(action_codes, list):
                        return Response(
                            {'error': f'Actions for module {module_code} must be a list'}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # Check if module exists
                    try:
                        module = Module.objects.get(code=module_code, is_active=True)
                    except Module.DoesNotExist:
                        return Response(
                            {'error': f'Module not found: {module_code}'}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # Check if actions exist
                    existing_actions = Action.objects.filter(code__in=action_codes, is_active=True)
                    found_action_codes = set(existing_actions.values_list('code', flat=True))
                    requested_action_codes = set(action_codes)
                    missing_action_codes = requested_action_codes - found_action_codes
                    
                    if missing_action_codes:
                        return Response(
                            {'error': f'Actions not found for module {module_code}: {", ".join(missing_action_codes)}'}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # Get permissions for this module+actions combination
                    permissions = Permission.objects.filter(
                        module=module,
                        action__code__in=action_codes,
                        is_active=True
                    )
                    
                    # Add these permissions to the role
                    role.permissions.add(*permissions)
            
            # Prepare response data
            modules_data = []
            
            # Get all modules that have any access (either full or specific permissions)
            all_role_modules = Module.objects.filter(
                Q(roles=role) | Q(permissions__roles=role),
                is_active=True
            ).distinct()
            
            for module in all_role_modules:
                # Get specific permissions for this module
                module_permissions = role.permissions.filter(
                    module=module,
                    is_active=True
                )
                
                access_actions = list(module_permissions.values_list('action__code', flat=True))
                
                modules_data.append({
                    'code': module.code,
                    'name': module.name,
                    'description': module.description,
                    'access': access_actions
                })
            
            return Response({
                'message': f'Role {role.name} updated successfully',
                'role_id': role.id,
                'role_name': role.name,
                'role_description': role.description,
                'modules': {
                    'data': modules_data
                }
            })
            
        except Role.DoesNotExist:
            return Response(
                {'error': 'Role not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def get(self, request):
        """Get role's current modules and permissions"""
        role_id = request.GET.get('role_id')
        print(role_id)
        
        if not role_id:
            return Response(
                {'error': 'role_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            role = Role.objects.get(id=role_id)
            
            # Get modules and organize access by module
            modules_data = []
            
            # Get modules directly assigned to role
            role_modules = role.modules.filter(is_active=True)
            
            # Get all modules that have permissions assigned to this role
            permission_modules = Module.objects.filter(
                permissions__roles=role,
                is_active=True
            ).distinct()
            
            # Combine both sets of modules
            all_modules = (role_modules | permission_modules).distinct()
            
            for module in all_modules:
                # Get actions/permissions for this module
                module_permissions = role.permissions.filter(
                    module=module,
                    is_active=True
                )
                
                access_actions = list(module_permissions.values_list('action__code', flat=True))
                
                # If module is directly assigned, it might have full access
                # But we only show specific permissions that are assigned
                modules_data.append({
                    'code': module.code,
                    'name': module.name,
                    'description': module.description,
                    'access': access_actions
                })
            
            return Response({
                'role_id': role.id,
                'role_name': role.name,
                'role_description': role.description,
                'modules': {
                    'data': modules_data
                }
            })
            
        except Role.DoesNotExist:
            return Response(
                {'error': 'Role not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
