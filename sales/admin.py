from django.contrib import admin
from .models import Transaction, TransactionItem


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "total_amount",
        "created_at",
        "created_by",
        "discount_applied",
        "promotion_applied",
        "customer",
    )


@admin.register(TransactionItem)
class TransactionItemAdmin(admin.ModelAdmin):
    list_display = ("transaction", "product", "quantity", "total_amount")
