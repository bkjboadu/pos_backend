from django.db import models
from sales.models import Transaction
from django.core.exceptions import ValidationError


class Payment(models.Model):
    PAYMENT_METHODS = [("cash", "Cash"), ("card", "Card")]
    transaction = models.OneToOneField(
        Transaction, on_delete=models.CASCADE, related_name="payment"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    paid_at = models.DateTimeField(auto_now_add=True)

    # Stripe-specific fields (only used for card payments)
    stripe_charge_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_status = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Payment for Transaction #{self.transaction.id} ({self.payment_method})"

    def clean(self):
        if self.amount < self.transaction.total_amount:
            raise ValueError(f"Paid Amount {self.amount} is less than the total amount {self.transaction.total_amount}.")

        if self.payment_method == "card":
            if not self.stripe_charge_id or not self.stripe_status:
                raise ValidationError(
                    "Stripe details (charge ID and status) are required for card payments."
                )
        elif self.payment_method == "cash":
            if self.stripe_charge_id or self.stripe_status:
                raise ValidationError(
                    "Stripe details should not be provided for cash payments."
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
