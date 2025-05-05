from django import forms

from accounts.models import Employee
from core.models import (
    Attendance,
    Bonuses,
    Deductions,
    SalaryCalculations,
    SalaryStructure,
)


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "name",
            "position",
            "department",
            "contact_number",
            "bank_account_num",
            "status",
            "employment_date",
        ]


class SalaryStructureForm(forms.ModelForm):
    class Meta:
        model = SalaryStructure
        fields = ["employee", "basic_salary", "overtime_rate", "bonus_percentage"]
        widgets = {
            "basic_salary": forms.NumberInput(attrs={"step": "0.01"}),
            "overtime_rate": forms.NumberInput(attrs={"step": "0.01"}),
            "bonus_percentage": forms.NumberInput(attrs={"step": "0.01"}),
        }


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ["employee", "date", "shift", "hours_worked", "overtime_hours", "is_present"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "hours_worked": forms.NumberInput(attrs={"step": "0.01"}),
            "overtime_hours": forms.NumberInput(attrs={"step": "0.01"}),
        }


class DeductionsForm(forms.ModelForm):
    class Meta:
        model = Deductions
        fields = ["employee", "date", "reason", "amount"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "amount": forms.NumberInput(attrs={"step": "0.01"}),
        }


class BonusesForm(forms.ModelForm):
    class Meta:
        model = Bonuses
        fields = ["employee", "date", "reason", "amount"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "amount": forms.NumberInput(attrs={"step": "0.01"}),
        }


class SalaryCalculationsForm(forms.ModelForm):
    class Meta:
        model = SalaryCalculations
        fields = [
            "employee",
            "month",
            "total_hours",
            "overtime_hours",
            "total_deductions",
            "total_bonuses",
            "net_salary",
        ]
        widgets = {
            "month": forms.DateInput(attrs={"type": "date"}),
            "total_hours": forms.NumberInput(attrs={"step": "0.01"}),
            "overtime_hours": forms.NumberInput(attrs={"step": "0.01"}),
            "total_deductions": forms.NumberInput(attrs={"step": "0.01"}),
            "total_bonuses": forms.NumberInput(attrs={"step": "0.01"}),
            "net_salary": forms.NumberInput(attrs={"step": "0.01"}),
        }
