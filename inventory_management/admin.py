from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        "name",
        "barcode",
        "image",
        "price",
        "stock",
        "branch",
        "category",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
    )
