from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from .services import RBACService


def require_permission(module_code, action_code):
    """
    Decorator to check if user has specific permission for a view
    Usage: @require_permission('dashboard', 'view')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            if not RBACService.user_has_permission(request.user, module_code, action_code):
                return Response(
                    {
                        'error': f'You do not have permission to {action_code} {module_code}',
                        'required_permission': f'{module_code}_{action_code}'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            return view_func(self, request, *args, **kwargs)
        return _wrapped_view
    return decorator


def require_any_permission(*permission_tuples):
    """
    Decorator to check if user has any of the specified permissions
    Usage: @require_any_permission(('dashboard', 'view'), ('reports', 'view'))
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            user = request.user
            has_permission = any(
                RBACService.user_has_permission(user, module, action)
                for module, action in permission_tuples
            )
            
            if not has_permission:
                return Response(
                    {
                        'error': 'You do not have sufficient permissions to access this resource',
                        'required_permissions': [f'{module}_{action}' for module, action in permission_tuples]
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            return view_func(self, request, *args, **kwargs)
        return _wrapped_view
    return decorator


class RBACPermission:
    """
    Permission class for Django REST Framework views
    Usage in view: permission_classes = [RBACPermission('dashboard', 'view')]
    """
    def __init__(self, module_code, action_code):
        self.module_code = module_code
        self.action_code = action_code

    def __call__(self):
        class Permission:
            def has_permission(self, request, view):
                return RBACService.user_has_permission(
                    request.user, self.module_code, self.action_code
                )
        return Permission()
