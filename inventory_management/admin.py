from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'barcode', 'image', 'price', 'stock', 'created_at', 'created_by','updated_at', 'updated_by')
