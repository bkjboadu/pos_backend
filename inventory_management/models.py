from django.db import models
from django.core.exceptions import ValidationError
from users.models import CustomUser


class Product(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='images/',null=True, blank=True)
    barcode = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        CustomUser,
        related_name="products_created",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        CustomUser,
        related_name="products_updated",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.name}"
