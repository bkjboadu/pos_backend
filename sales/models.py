from django.db import models
from inventory_management.models import Product
from users.models import CustomUser


class Transaction(models.Model):
    PAYMENT_METHODS = [
        ("cash", "Cash"),
        ("card", "Card"),
    ]

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        CustomUser,
        related_name="transaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Transaction #{self.id} at {self.branch.name}"

    def save(self, *args, **kwargs):
        self.total_amount = sum(item.price * item.quantity for item in self.items.all())
        super().save(*args, **kwargs)


class TransactionItem(models.Model):
    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Transaction #{self.transaction.id})"

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.product.stock -= self.quantity
            if self.product.stock < 0:
                raise ValueError("Insufficient stock for product")
            self.product.save()
        super().save(*args, **kwargs)
