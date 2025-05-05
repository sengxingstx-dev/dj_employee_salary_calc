from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Attendance, Employee


class Command(BaseCommand):
    help = "Updates attendance records for employees who did not scan in"

    def handle(self, *args, **options):
        today = timezone.now().date()
        employees = Employee.objects.all()

        for employee in employees:
            attendance, created = Attendance.objects.get_or_create(
                employee=employee,
                date=today,
                defaults={
                    "shift": "Absent",
                    "hours_worked": 0,
                    "overtime_hours": 0,
                    "is_present": False,
                },
            )

            if created or not attendance.scan_in_time:
                attendance.is_present = False
                attendance.save()
                self.stdout.write(
                    self.style.SUCCESS(f"Marked {employee.name} as absent for {today}")
                )

        self.stdout.write(self.style.SUCCESS("Successfully updated attendance records"))
