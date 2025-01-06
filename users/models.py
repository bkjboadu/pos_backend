import uuid
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)


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


    role = models.CharField(
        max_length=50,
        choices=[
            ("cashier", "Cashier"),
            ("manager", "Manager"),
        ],
        default=None,  # Default is no role
        null=True,
        blank=True,
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.email} - {self.role}"



class BlacklistedToken(models.Model):
    token = models.CharField(max_length=255, unique=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token

    class Meta:
        db_table = "blacklisted_tokens"
