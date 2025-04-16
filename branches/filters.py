import django_filters
from .models import Branch
from django_filters import DateFromToRangeFilter


class BranchFilter(django_filters.FilterSet):
    id = django_filters.NumberFilter(field_name='id')
    created_at = DateFromToRangeFilter(label="Created Date Range")
    updated_at = DateFromToRangeFilter(label="Updated Date Range")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    address = django_filters.CharFilter(field_name="address", lookup_expr="icontains")
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Branch
        fields = [
            "id",
            "name",
            "address",
            "created_at",
            "updated_at",
            "is_active",
        ]
