import pytz
from django.core.validators import MinValueValidator
from django.db import models

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
        max_digits=5, decimal_places=2, validators=[MinValueValidator(0)]
    )
    overtime_hours = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[MinValueValidator(0)]
    )
    is_present = models.BooleanField(default=True)
    scan_in_time = models.DateTimeField(null=True, blank=True)
    scan_out_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Attendance for {self.employee.name} on {self.date}"

    def calculate_hours_worked(self):
        if self.scan_in_time and self.scan_out_time:
            tz = pytz.timezone("Asia/Vientiane")
            scan_in = self.scan_in_time.astimezone(tz)
            scan_out = self.scan_out_time.astimezone(tz)
            duration = scan_out - scan_in
            self.hours_worked = duration.total_seconds() / 3600
            self.save()


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
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="salary_calculations"
    )
    month = models.DateField()  # Stores the first day of the month (e.g., "2024-11-01")
    total_hours = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    overtime_hours = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    total_deductions = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    total_bonuses = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    net_salary = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return f"Salary Calculation for {self.employee.name} for {self.month.strftime('%B %Y')}"
