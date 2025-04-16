import django_filters
from .models import CustomUser

class CustomUserFilter(django_filters.FilterSet):
    email = django_filters.CharFilter(field_name='email', lookup_expr='icontains')
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    phone_number = django_filters.CharFilter(lookup_expr='icontains')
    role = django_filters.ChoiceFilter(choices=CustomUser._meta.get_field("role").choices)
    branches = django_filters.UUIDFilter(field_name='branch__id')  # or CharFilter if you want to search by name
    is_active = django_filters.BooleanFilter()
    date_joined = django_filters.DateFromToRangeFilter()

    class Meta:
        model = CustomUser
        fields = [
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'role',
            'branches',
            'is_active',
            'date_joined'
        ]
