from django.db import models
from django.core.exceptions import ValidationError
from users.models import CustomUser
from storages.backends.gcloud import GoogleCloudStorage
from datetime import datetime


class Product(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to="images/",
        null=True,
        blank=True,
        storage=GoogleCloudStorage()
    )
    barcode = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        CustomUser,
        related_name="created_products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        CustomUser,
        related_name="updated_products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.name}"


class StockInput(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="stock_inputs",
        on_delete=models.CASCADE
    )
    added_by = models.ForeignKey(
        CustomUser,
        related_name="stock_inputs",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    quantity = models.PositiveIntegerField()
    date_added = models.DateTimeField(default=datetime.now)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} added to {self.product.name} on {self.date_added}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.product.stock += self.quantity
            self.product.save()
        super().save(*args, **kwargs)
