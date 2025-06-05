import pytz
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from accounts.models import Employee
from common.models import BaseModel


class SalaryStructure(BaseModel):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="salary_structures"
    )
    basic_salary = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    overtime_rate = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    bonus_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return f"Salary Structure for {self.employee.name}"


class Attendance(BaseModel):
    SHIFT_CHOICES = [
        ("Morning", "Morning"),
        ("Afternoon", "Afternoon"),
        ("Night", "Night"),
        ("Absent", "Absent"),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="attendances")
    date = models.DateField()
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES)
    hours_worked = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], default=0
    )
    overtime_hours = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], default=0
    )
    is_present = models.BooleanField(default=True)
    scan_in_time = models.DateTimeField(null=True, blank=True)
    scan_out_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Attendance for {self.employee.name} on {self.date}"

    def calculate_hours_worked(self):
        if self.scan_in_time and self.scan_out_time:
            # tz = pytz.timezone("Asia/Vientiane")
            # scan_in = self.scan_in_time.astimezone(tz)
            # scan_out = self.scan_out_time.astimezone(tz)
            # duration = scan_out - scan_in
            # self.hours_worked = duration.total_seconds() / 3600
            # self.save()

            # If already timezone-aware:
            if timezone.is_naive(self.scan_in_time) and timezone.is_naive(self.scan_out_time):
                # Fallback or raise error if times are naive and timezone isn't specified
                # This part depends on how scan_in_time/scan_out_time are stored.
                # Assuming they are already localized or UTC for this calculation.
                pass

            duration = self.scan_out_time - self.scan_in_time
            self.hours_worked = duration.total_seconds() / 3600
            self.save(update_fields=["hours_worked"])  # More efficient save


class Deductions(BaseModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="deductions")
    date = models.DateField()
    reason = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"Deduction for {self.employee.name} on {self.date}"


class Bonuses(BaseModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="bonuses")
    date = models.DateField()
    reason = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"Bonus for {self.employee.name} on {self.date}"


class SalaryCalculations(BaseModel):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("FAILED", "Failed to Generate"),
    ]
    PAYMENT_METHOD_CHOICES = [
        ("BANK_TRANSFER", "Bank Transfer"),
        ("CASH", "Cash"),
        ("CHEQUE", "Cheque"),
        ("OTHER", "Other"),
    ]

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="salary_calculations"
    )
    month_year = models.DateField()  # Stores the first day of the month (e.g., "2024-11-01")
    # Snapshots at the time of calculation
    basic_salary_snapshot = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0
    )
    overtime_rate_snapshot = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0
    )

    # Calculated values
    total_hours_worked = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0
    )

    total_overtime_hours = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0
    )
    total_deductions_amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0
    )
    total_bonuses_amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0
    )

    gross_salary = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0
    )

    net_salary = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0
    )

    # Status and payment details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    generated_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("employee", "month_year")  # Ensure one record per employee per month
        ordering = ["-month_year", "employee__name"]

    def __str__(self):
        return (
            f"Salary Calculation for {self.employee.name} for {self.month_year.strftime('%B %Y')}"
        )

    # The field 'month' was renamed to 'month_year' to avoid conflict with the property
    @property
    def month_display(self):
        return self.month_year.strftime("%B")

    @property
    def year_display(self):
        return self.month_year.strftime("%Y")
