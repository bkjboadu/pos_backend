from django.contrib import admin
from .models import Category

@admin.register(Category)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        "name",
        "description"
    )
