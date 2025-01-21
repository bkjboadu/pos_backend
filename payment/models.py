from django.db import models
from sales.models import Transaction
from django.core.exceptions import ValidationError


class Payment(models.Model):
    PAYMENT_METHODS = [("cash", "Cash"), ("card", "Card"), ("Split", "Split")]
    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name="payment"
    )
    total_payment = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    paid_at = models.DateTimeField(auto_now_add=True)

    # Fields for Cash Payments
    cash_payment = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, default=0
    )

    # Fields for Card Payments
    card_payment = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, default=0
    )

    # Stripe-specific fields (only used for card payments)
    stripe_charge_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_status = models.CharField(max_length=255, null=True, blank=True)

    balance_returned = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Payment for Transaction #{self.transaction.id} ({self.payment_method})"

    def clean(self):
        # Validate total amount matches cash + card payments
        self.total_payment = (self.cash_payment or 0) + (self.card_payment or 0)

        if self.total_payment < self.transaction.total_amount:
            raise ValueError(
                f"Paid Amount {self.amount} is less than the total amount {self.transaction.total_amount}."
            )

        if self.payment_method == "card":
            if not self.stripe_charge_id or not self.stripe_status:
                raise ValidationError(
                    "Stripe details (charge ID and status) are required for card payments."
                )

        # Validate payment details for specific methods
        if self.payment_method == "cash" and self.card_payment > 0:
            raise ValidationError(
                "Card payment should not be provided for cash-only payments."
            )
        if self.payment_method == "card" and self.cash_payment > 0:
            raise ValidationError(
                "Cash payment should not be provided for card-only payments."
            )

        if self.payment_method == "card":
            if not self.stripe_charge_id or not self.stripe_status:
                raise ValidationError("Stripe details are required for card payments.")
        if self.payment_method == "cash" and (
            self.stripe_charge_id or self.stripe_status
        ):
            raise ValidationError(
                "Stripe details should not be provided for cash payments."
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
