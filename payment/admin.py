from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "total_payment",
        "transaction",
        "payment_method",
        "cash_payment",
        "card_payment",
        "paid_at",
        "stripe_charge_id",
        "stripe_status",
    )
