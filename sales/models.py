from django.db import models
from django.utils.timezone import now
from inventory_management.models import Product
from discounts.models import Discount, Promotion
from users.models import CustomUser
from customers.models import Customer
from .managers import TransactionManager


class Transaction(models.Model):
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        CustomUser,
        related_name="created_transaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        CustomUser,
        related_name="updated_transaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    discount_applied = models.ForeignKey(
        Discount,
        related_name="transactions",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    promotion_applied = models.ForeignKey(
        Promotion,
        related_name="transactions",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    customer = models.ForeignKey(
        Customer,
        related_name="transaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    objects = TransactionManager()

    def __str__(self):
        return f"Transaction #{self.id}"

    def save(self, *args, **kwargs):
        # Save the instance first to ensure it has a primary key
        if not self.pk:
            super().save(*args, **kwargs)
        else:
            if self.total_amount == 0:
                self.total_amount = sum(
                    item.product.price * item.quantity for item in self.items.all()
                )
            super().save(*args, **kwargs)


class TransactionItem(models.Model):
    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Transaction #{self.transaction.id})"

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.product.stock -= self.quantity
            self.total_amount = self.quantity*self.product.price
            if self.product.stock < 0:
                raise ValueError("Insufficient stock for product")
            self.product.save()
        self.total_amount = self.quantity*self.product.price
        super().save(*args, **kwargs)
