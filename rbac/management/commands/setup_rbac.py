from django.core.management.base import BaseCommand
from django.db.models import Q
from rbac.models import Module, Action, Permission, Role
from rbac.services import RBACService
from users.models import CustomUser


class Command(BaseCommand):
    help = 'Setup RBAC system with default modules, actions, permissions, and roles'

    def handle(self, *args, **options):
        self.stdout.write('Setting up RBAC system...')

        # Create modules
        modules_data = [
            {'name': 'Dashboard', 'code': 'dashboard', 'description': 'Dashboard overview and analytics'},
            {'name': 'Staff Management', 'code': 'staff', 'description': 'User and staff management'},
            {'name': 'POS', 'code': 'pos', 'description': 'Point of Sale transactions'},
            {'name': 'Branches', 'code': 'branches', 'description': 'Branch management'},
            {'name': 'Customers', 'code': 'customers', 'description': 'Customer management'},
            {'name': 'Reports', 'code': 'reports', 'description': 'Reports and analytics'},
            {'name': 'Settings', 'code': 'settings', 'description': 'System settings'},
        ]

        for module_data in modules_data:
            module, created = Module.objects.get_or_create(
                code=module_data['code'],
                defaults=module_data
            )
            if created:
                self.stdout.write(f'Created module: {module.name}')

        # Create actions
        actions_data = [
            {'name': 'View', 'code': 'view', 'description': 'View records'},
            {'name': 'Create', 'code': 'create', 'description': 'Create new records'},
            {'name': 'Edit', 'code': 'edit', 'description': 'Edit existing records'},
            {'name': 'Delete', 'code': 'delete', 'description': 'Delete records'},
        ]

        for action_data in actions_data:
            action, created = Action.objects.get_or_create(
                code=action_data['code'],
                defaults=action_data
            )
            if created:
                self.stdout.write(f'Created action: {action.name}')

        # Create permissions (module + action combinations)
        modules = Module.objects.all()
        actions = Action.objects.all()

        for module in modules:
            for action in actions:
                permission_name = f'{module.name} {action.name}'
                permission_code = f'{module.code}_{action.code}'
                
                permission, created = Permission.objects.get_or_create(
                    module=module,
                    action=action,
                    defaults={
                        'name': permission_name,
                        'code': permission_code
                    }
                )
                if created:
                    self.stdout.write(f'Created permission: {permission.name}')

        # Create roles with permissions
        self.create_roles()

        # Sync existing users with RBAC roles
        self.sync_existing_users()

        self.stdout.write(self.style.SUCCESS('RBAC system setup completed!'))

    def create_roles(self):
        """Create default roles with their permissions"""
        
        # Admin Manager - All permissions
        admin_role, created = Role.objects.get_or_create(
            code='admin_manager',
            defaults={
                'name': 'Admin Manager',
                'description': 'Full system access'
            }
        )
        if created:
            admin_role.permissions.set(Permission.objects.all())
            self.stdout.write(f'Created role: {admin_role.name}')

        # Manager - Most permissions except some sensitive ones
        manager_permissions = Permission.objects.exclude(
            Q(module__code='settings', action__code='delete')
        )
        
        manager_role, created = Role.objects.get_or_create(
            code='manager',
            defaults={
                'name': 'Manager',
                'description': 'Branch management access'
            }
        )
        if created:
            manager_role.permissions.set(manager_permissions)
            self.stdout.write(f'Created role: {manager_role.name}')

        # Cashier - Limited permissions
        cashier_permissions = Permission.objects.filter(
            Q(module__code='dashboard', action__code='view') |
            Q(module__code='pos') |
            Q(module__code='customers', action__code__in=['view', 'create', 'edit'])
        )
        
        cashier_role, created = Role.objects.get_or_create(
            code='cashier',
            defaults={
                'name': 'Cashier',
                'description': 'Point of sale access'
            }
        )
        if created:
            cashier_role.permissions.set(cashier_permissions)
            self.stdout.write(f'Created role: {cashier_role.name}')

    def sync_existing_users(self):
        """Sync existing users with RBAC roles based on their legacy role field"""
        users = CustomUser.objects.all()
        for user in users:
            if user.role:
                try:
                    rbac_role = Role.objects.get(code=user.role)
                    user_role, created = RBACService.assign_role_to_user(user, rbac_role)
                    if created:
                        self.stdout.write(f'Assigned role {rbac_role.name} to user {user.email}')
                except Role.DoesNotExist:
                    self.stdout.write(f'Warning: Role {user.role} not found for user {user.email}')
