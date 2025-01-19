from django.db import models
from users.models import CustomUser

class Branch(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(null=True,blank=True)
    created_by = models.ForeignKey(
        CustomUser,
        related_name='created_branches',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_by = models.ForeignKey(
        CustomUser,
        related_name='updated_branches',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
