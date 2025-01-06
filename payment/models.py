from django.db import models
from inventory_management.models import Transaction


class StripePayment(models.Model):
    order = models.ForeignKey(Transaction, on_delete=models.SET_NULL)
    stripe_charge_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order {self.order.id}"
