from django.db import models
from companies.models import Branch


class Product(models.Model):
    name = models.CharField(max_length=255)
    barcode = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="products"
    )  # Scoped to a branch
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.branch.name})"
