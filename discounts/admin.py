from django.contrib import admin
from .models import Discount, Promotion


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_type",
        "value",
        "start_date",
        "end_date",
        "is_active",
    )


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ("name", "discount", "start_date", "end_date", "is_active")
