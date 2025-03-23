import django_filters
from .models import Order
from django_filters import DateFromToRangeFilter


class OrderFilter(django_filters.FilterSet):
    created_at = DateFromToRangeFilter(label="Created Date Range")
    status = django_filters.CharFilter(field_name="status", lookup_expr='iexact')
    payment_status = django_filters.CharFilter(field_name="payment_status", lookup_expr='iexact')
    email = django_filters.CharFilter(field_name="email", lookup_expr='icontains')
    name = django_filters.CharFilter(field_name="name", lookup_expr='icontains')
    order_number = django_filters.UUIDFilter(field_name="order_number")
    return_requested = django_filters.BooleanFilter()
    return_approved = django_filters.BooleanFilter()

    class Meta:
        model = Order
        fields = [
            "status",
            "payment_status",
            "created_at",
            "email",
            "name",
            "order_number",
            "return_requested",
            "return_approved",
        ]
