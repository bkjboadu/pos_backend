from django.contrib import admin
from .models import CustomUser, BlacklistedToken


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "get_branches",
        "is_active",
        "is_staff",
        "is_superuser",
        "phone_number",
        "date_joined",
        "last_login",
    )

    def get_branches(self, obj):
        return ", ".join([branch.name for branch in obj.branches.all()])

    get_branches.short_description = "Branches"


@admin.register(BlacklistedToken)
class BlacklistedTokenAdmin(admin.ModelAdmin):
    list_display = ("token", "blacklisted_at")
