# from django.contrib import admin
# from .models import CustomUser

# admin.site.register(CustomUser)

from django.contrib import admin

# from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, BlacklistedToken


admin.site.register(CustomUser)
admin.site.register(BlacklistedToken)
# from django.contrib.auth.forms import UserCreationForm, UserChangeForm

# # Custom forms for UserAdmin
# class CustomUserCreationForm(UserCreationForm):
#     class Meta:
#         model = CustomUser
#         fields = ('email', 'first_name', 'last_name', 'role')

# class CustomUserChangeForm(UserChangeForm):
#     class Meta:
#         model = CustomUser
#         fields = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'is_superuser')

# # Custom UserAdmin
# class CustomUserAdmin(UserAdmin):
#     add_form = CustomUserCreationForm
#     form = CustomUserChangeForm
#     model = CustomUser

#     # Display fields in the admin list view
#     list_display = ('email', 'first_name', 'last_name', 'role','is_active', 'is_staff', 'is_superuser')
#     list_filter = ('is_staff', 'is_superuser', 'is_active', 'role')

#     # Fields to display when viewing or editing a user
#     fieldsets = (
#         (None, {'fields': ('email', 'password')}),
#         ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number')}),
#         ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
#         ('Company Info', {'fields': ( 'role')}),
#         ('Important Dates', {'fields': ('last_login', 'date_joined')}),
#     )

#     # Fields to display when creating a user
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'is_superuser'),
#         }),
#     )

#     search_fields = ('email', 'first_name', 'last_name')
#     ordering = ('email',)

# # Register the CustomUser model with the CustomUserAdmin
# admin.site.register(CustomUser, CustomUserAdmin)

# # Optional: Register BlacklistedToken if needed
# @admin.register(BlacklistedToken)
# class BlacklistedTokenAdmin(admin.ModelAdmin):
#     list_display = ('token', 'blacklisted_at')
#     search_fields = ('token',)
#     ordering = ('-blacklisted_at',)
