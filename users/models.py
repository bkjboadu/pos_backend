import uuid
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from companies.models import Company


class CustomUserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    def create_user(self, email, password=None, *args, **kwargs):
        if not email:
            raise ValueError("Email Address is Required")

        if not password:
            raise ValueError("Password is Required")

        email = self.normalize_email(email)
        user = self.model(email=email, *args, **kwargs)
        user.set_password(password)
        try:
            user.save(using=self._db)
            return user
        except Exception as e:
            raise ValueError(f"An error occurred while creating the user: {e}")

    def create_company_admin(self, email, password, company, *args, **kwargs):
        """
        Create a company-specific admin.
        """
        if not company:
            raise ValueError("Company is required for a company admin.")
        return self.create_user(
            email=email,
            password=password,
            company=company,
            role="company_admin",
            *args,
            **kwargs,
        )

    def create_superuser(self, email, first_name, password=None, *args, **kwargs):
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)

        if kwargs.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if kwargs.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(
            email=email, password=password, first_name=first_name, *args, **kwargs
        )


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    # Company and branch fields
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="users",
        help_text="The company this user is associated with. Null for system-wide superusers.",
    )

    # Added fields for POS System
    branch = models.ForeignKey(
        "companies.Branch",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="employees",
    )
    role = models.CharField(
        max_length=50,
        choices=[
            ("company_admin", "Company Admin"),
            ("cashier", "Cashier"),
            ("branch_manager", "Branch Manager"),
        ],
        default=None,  # Default is no role
        null=True,
        blank=True,
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        if self.is_superuser:
            return f"{self.email} - Superuser"
        elif self.role == "company_admin":
            return f"{self.email} ({self.role}) - ({self.company.name})"
        elif self.role == "cashier":
            return (
                f"{self.email} ({self.role}) - ({self.company.name}) - ({self.branch})"
            )
        elif self.role == "branch_manager":
            return (
                f"{self.email} ({self.role}) - ({self.company.name}) - ({self.branch})"
            )

    def save(self, *args, **kwargs):
        # Enforce branch validation
        if not self.is_superuser:
            if self.role == "company_admin" and self.branch is not None:
                raise ValueError("A company_admin cannot be associated with a branch.")
            if self.role != "company_admin":
                if self.branch is None:
                    raise ValueError(
                        "Non-superuser and non company_admin accounts must be associated with a branch"
                    )
                if self.branch.company != self.company:
                    raise ValueError(
                        "The selected branch does not belong to the selected company"
                    )
            if (
                not self.is_superuser
                and self.branch is None
                and self.role != "company_admin"
            ):
                raise ValueError(
                    "Non-superuser accounts must be associated with a branch"
                )
        super().save(*args, **kwargs)


class BlacklistedToken(models.Model):
    token = models.CharField(max_length=255, unique=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token

    class Meta:
        db_table = "blacklisted_tokens"
