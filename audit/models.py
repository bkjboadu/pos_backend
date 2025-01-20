from django.db import models
from users.models import CustomUser
from django.utils.timezone import now


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("login", "Login"),
        ("logout", "Logout"),
        ("other", "Other"),
    ]

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )
    action_time = models.DateTimeField(default=now)
    resource_name = models.CharField(max_length=255)
    resource_id = models.PositiveIntegerField(null=True, blank=True)
    details = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.action} on {self.resource_name} by {self.performed_by} at {self.action_time}"
