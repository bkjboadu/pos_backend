import django_filters
from inventory_management.models import Product

class ProductFilter(django_filters.FilterSet):
    branch = django_filters.NumberFilter(field_name='branch')
    class Meta:
        model = Product
        fields = {
            'name': ['icontains'],
            'sku': ['exact'],
            'price': ['exact', 'lt', 'gt'],
            'stock': ['exact', 'lt', 'gt'],
            'barcode': ['exact'],
            'branch': ['exact'],
            'category': ['exact']
        }
