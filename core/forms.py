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
            "employee",  # Should be non-editable after creation
            "month_year",  # Should be non-editable after creation
            "basic_salary_snapshot",
            "overtime_rate_snapshot",
            "total_hours_worked",
            "total_overtime_hours",
            "total_deductions_amount",
            "total_bonuses_amount",
            "gross_salary",
            "net_salary",
            "status",
            "payment_method",
            "paid_at",
            "notes",
        ]
        labels = {
            "employee": "ພະນັກງານ",
            "month_year": "ເດືອນ/ປີ",
            "basic_salary_snapshot": "ເງິນເດືອນພື້ນຖານ",
            "overtime_rate_snapshot": "ອັດຕາ OT",
            "total_hours_worked": "ຊົ່ວໂມງເຮັດວຽກທັງໝົດ",
            "total_overtime_hours": "ຊົ່ວໂມງ OT ທັງໝົດ",
            "total_deductions_amount": "ຍອດຫັກທັງໝົດ",
            "total_bonuses_amount": "ຍອດໂບນັດທັງໝົດ",
            "gross_salary": "ເງິນເດືອນລວມຍອດ",
            "net_salary": "ເງິນເດືອນສຸດທິ",
            "status": "ສະຖານະ",
            "payment_method": "ວິທີການຊຳລະເງິນ",
            "paid_at": "ຊຳລະເມື່ອ",
            "notes": "ໝາຍເຫດ",
        }
        widgets = {
            # Make most fields readonly when editing, focus on status & payment
            "employee": forms.Select(attrs={"readonly": "readonly", "disabled": "disabled"}),
            "month_year": forms.DateInput(attrs={"type": "date", "readonly": "readonly"}),
            "basic_salary_snapshot": forms.NumberInput(
                attrs={"readonly": "readonly", "step": "0.01"}
            ),
            "overtime_rate_snapshot": forms.NumberInput(
                attrs={"readonly": "readonly", "step": "0.01"}
            ),
            "total_hours_worked": forms.NumberInput(attrs={"readonly": "readonly", "step": "0.01"}),
            "total_overtime_hours": forms.NumberInput(
                attrs={"readonly": "readonly", "step": "0.01"}
            ),
            "total_deductions_amount": forms.NumberInput(
                attrs={"readonly": "readonly", "step": "0.01"}
            ),
            "total_bonuses_amount": forms.NumberInput(
                attrs={"readonly": "readonly", "step": "0.01"}
            ),
            "gross_salary": forms.NumberInput(attrs={"readonly": "readonly", "step": "0.01"}),
            "net_salary": forms.NumberInput(attrs={"readonly": "readonly", "step": "0.01"}),
            "paid_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If instance exists, make employee and month_year truly readonly
        if self.instance and self.instance.pk:
            self.fields["employee"].disabled = True
            self.fields["month_year"].disabled = True
            # Pre-fill paid_at with now if status is being changed to PAID and paid_at is not set
            # This logic might be better in the view.
        self.fields["paid_at"].required = False  # Make it optional

    def clean_paid_at(self):
        paid_at = self.cleaned_data.get("paid_at")
        status = self.cleaned_data.get("status")
        if status == "PAID" and not paid_at:
            # If marking as PAID and paid_at is empty, default to now
            # However, allowing user to set it is also fine.
            # For now, let's make it required if status is PAID.
            # raise forms.ValidationError("Paid At date is required when status is PAID.")
            pass  # Or default to timezone.now() if you prefer auto-filling
        return paid_at
