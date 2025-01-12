from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "amount",
        "transaction",
        "payment_method",
        "paid_at",
        "stripe_charge_id",
        "stripe_status",
    )
