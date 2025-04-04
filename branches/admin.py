from django.contrib import admin
from .models import Branch


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "address",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
    )
