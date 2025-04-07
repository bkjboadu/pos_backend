import django_filters
from .models import AuditLog

class AuditLogFilter(django_filters.FilterSet):
    action = django_filters.CharFilter(lookup_expr='icontains')
    performed_by__first_name = django_filters.CharFilter(lookup_expr='icontains')
    resource_name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = AuditLog
        fields = [
            'action',
            'performed_by__first_name',
            'action_time',
            'resource_name',
            'resource_id',
        ]
