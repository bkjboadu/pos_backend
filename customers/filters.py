import django_filters
from .models import Customer
from django_filters import DateFromToRangeFilter


class CustomerFilter(django_filters.FilterSet):
    created_at = DateFromToRangeFilter(label="Created Date Range")
    first_name = django_filters.CharFilter(field_name="first_name", lookup_expr="icontains")
    last_name = django_filters.CharFilter(field_name="last_name", lookup_expr="icontains")
    email = django_filters.CharFilter(field_name="email", lookup_expr="icontains")
    phone_number = django_filters.CharFilter(field_name="phone_number", lookup_expr="icontains")
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Customer
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "created_at",
            "is_active",
        ]
