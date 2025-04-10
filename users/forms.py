from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser


class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = "__all__"

    def clean(self):
        print("Running form-level role validation...")
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        branches = cleaned_data.get("branches")

        if role == "cashier" and branches.count() != 1:
            raise ValidationError("Cashier must be assigned to exactly one branch.")

        if role == "manager" and branches.count() < 1:
            raise ValidationError("Manager must be assigned to at least one branch.")

        if role == "admin_manager" and branches.exists():
            raise ValidationError("Admin Manager must not be assigned to any branch.")

        return cleaned_data
