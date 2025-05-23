from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "created_at",
        "updated_at",
        "created_by",
    )
