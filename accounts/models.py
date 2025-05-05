from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone

from common.models import BaseModel


class AccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class Account(AbstractBaseUser, PermissionsMixin):
    username = None
    email = models.EmailField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = AccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email}"


class Employee(BaseModel):
    class EmployeeStatus(models.TextChoices):
        ACTIVE = "Active", "Active"
        INACTIVE = "Inactive", "Inactive"

    name = models.CharField(max_length=100, verbose_name="Full Name")
    position = models.CharField(max_length=100, verbose_name="Position")
    department = models.CharField(max_length=100, verbose_name="Department")
    contact_number = models.CharField(max_length=20, verbose_name="Contact Number")
    bank_account_num = models.CharField(max_length=100, verbose_name="Bank Account Number")
    status = models.CharField(
        max_length=20, choices=EmployeeStatus.choices, default=EmployeeStatus.ACTIVE
    )
    employment_date = models.DateField(verbose_name="Employment Date")
    user = models.OneToOneField(
        Account,
        on_delete=models.SET_NULL,
        related_name="employee_profile",
        verbose_name="Associated User",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.name}"
