from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditAdmin(admin.ModelAdmin):
    list_display = (
        "action",
        "performed_by",
        "action_time",
        "resource_name",
        "resource_id",
        "details"
    )
