from django.db import models
from django.utils.timezone import now
from users.models import CustomUser


class Discount(models.Model):
    code = models.CharField(max_length=255)
    discount_type = models.CharField(
        max_length=50, choices=[("percentage", "Percentage"), ("fixed", "Fixed Amount")]
    )
    value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField(default=now)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        CustomUser,
        related_name="discount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if self.end_date < now():
            self.is_active = False
        super().save(*args, **kwargs)


class Promotion(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    discount = models.ForeignKey(
        Discount, on_delete=models.CASCADE, related_name="promotions"
    )
    eligible_products = models.ManyToManyField(
        "inventory_management.Product", blank=True
    )
    start_date = models.DateTimeField(default=now)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
