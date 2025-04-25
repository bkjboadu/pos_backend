import django_filters
from .models import Transaction, TransactionItem
from django_filters import DateFromToRangeFilter, RangeFilter, CharFilter, NumberFilter


class TransactionFilter(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter()
    updated_at = django_filters.DateFromToRangeFilter()
    total_amount = django_filters.RangeFilter()
    branch = django_filters.NumberFilter(field_name='branch')
    created_by = django_filters.CharFilter(field_name='created_by__username', lookup_expr='icontains')
    updated_by = django_filters.CharFilter(field_name='updated_by__username', lookup_expr='icontains')
    customer = django_filters.CharFilter(field_name='customer__name', lookup_expr='icontains')
    discount_applied = django_filters.CharFilter(field_name='discount_applied__code', lookup_expr='icontains')
    promotion_applied = django_filters.CharFilter(field_name='promotion_applied__name', lookup_expr='icontains')

    class Meta:
        model = Transaction
        fields = [
            'branch',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
            'total_amount',
            'customer',
            'discount_applied',
            'promotion_applied',
        ]

class TransactionItemFilter(django_filters.FilterSet):
    transaction = django_filters.NumberFilter(field_name='transaction__id')  # <-- Add this line

    product = django_filters.CharFilter(field_name='product__name', lookup_expr='icontains')
    created_at = django_filters.DateFromToRangeFilter(field_name='transaction__created_at')
    updated_at = django_filters.DateFromToRangeFilter(field_name='transaction__updated_at')
    branch = django_filters.NumberFilter(field_name='transaction__branch')
    customer = django_filters.CharFilter(field_name='transaction__customer__name', lookup_expr='icontains')
    created_by = django_filters.CharFilter(field_name='transaction__created_by__username', lookup_expr='icontains')
    quantity = django_filters.RangeFilter()
    total_amount = django_filters.RangeFilter()

    class Meta:
        model = TransactionItem
        fields = [
            'transaction',        # <-- include it here too
            'product',
            'quantity',
            'total_amount',
            'created_at',
            'updated_at',
            'branch',
            'customer',
            'created_by'
        ]
