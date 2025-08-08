from django.urls import path
from .views import (
    UserAccessView,
    ModuleListView,
    ActionListView,
    RoleListView,
    AssignRoleView,
    RemoveRoleView,
    UpdateRoleAccessView,
    check_permission
)

urlpatterns = [
    path('user-access/', UserAccessView.as_view(), name='user-access'),
    path('modules/', ModuleListView.as_view(), name='modules'),
    path('actions/', ActionListView.as_view(), name='actions'),
    path('roles/', RoleListView.as_view(), name='roles'),
    path('assign-role/', AssignRoleView.as_view(), name='assign-role'),
    path('remove-role/', RemoveRoleView.as_view(), name='remove-role'),
    path('update-role-access/', UpdateRoleAccessView.as_view(), name='update-role-access'),
    path('check-permission/', check_permission, name='check-permission'),
]
