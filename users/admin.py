from django.contrib import admin
from .forms  import CustomUserForm
from .models import CustomUser, BlacklistedToken


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    form = CustomUserForm
    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "get_branches",
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
        "phone_number",
        "date_joined",
        "last_login",
    )

    filter_horizontal = ('branches',)

    def get_branches(self, obj):
        return ", ".join([branch.name for branch in obj.branches.all()])

    get_branches.short_description = "Branches"



@admin.register(BlacklistedToken)
class BlacklistedTokenAdmin(admin.ModelAdmin):
    list_display = ("token", "blacklisted_at")
