

from django.contrib import admin
from .models import CustomUser, BlacklistedToken


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'email','first_name', 'last_name',
        'is_active', 'is_staff', 'is_superuser',
        'phone_number', 'date_joined', 'last_login'
    )

@admin.register(BlacklistedToken)
class BlacklistedTokenAdmin(admin.ModelAdmin):
    list_display = ('token', 'blacklisted_tokens')
