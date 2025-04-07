import django_filters
from .models import Category

class CategoryFilter(django_filters.FilterSet):
    class Meta:
        name = django_filters.CharFilter(lookup_expr='icontains')
        description = django_filters.CharFilter(lookup_expr='icontains')

        model = Category
        fields = ['name', 'description']
