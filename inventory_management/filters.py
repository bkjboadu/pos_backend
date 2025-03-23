import django_filters
from inventory_management.models import Product

class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = {
            'name': ['icontains'],
            'sku': ['exact'],
            'price': ['exact', 'lt', 'gt'],
            'barcode': ['exact'],
        }
