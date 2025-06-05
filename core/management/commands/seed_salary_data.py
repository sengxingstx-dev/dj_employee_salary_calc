import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.utils import timezone

from accounts.models import Account, Employee
from core.models import (
    Attendance,
    Bonuses,
    Deductions,
    SalaryCalculations,
    SalaryStructure,
)


class Command(BaseCommand):
    help = "Seeds the database with sample salary calculation data"

    def handle(self, *args, **options):
        self.stdout.write("Starting to seed data...")

        # Clean up existing data to avoid duplicates if run multiple times
        # Be careful with this in a production environment!
        # SalaryCalculations.objects.all().delete()
        # Bonuses.objects.all().delete()
        # Deductions.objects.all().delete()
        # Attendance.objects.all().delete()
        # SalaryStructure.objects.all().delete()
        # Employee.objects.filter(name__startswith="Sample").delete() # Assuming sample employees have specific names
        # Account.objects.filter(email__contains="@sample.com").delete()

        self.stdout.write("Creating sample employees and salary structures...")

        sample_employees_data = [
            {
                "name": "Sample Employee One",
                "email_suffix": "one",
                "position": "Developer",
                "department": "IT",
                "basic_salary": 5000000,
                "overtime_rate": 50000,
            },
            {
                "name": "Sample Employee Two",
                "email_suffix": "two",
                "position": "Designer",
                "department": "Creative",
                "basic_salary": 4500000,
                "overtime_rate": 45000,
            },
            {
                "name": "Sample Employee Three",
                "email_suffix": "three",
                "position": "Manager",
                "department": "Management",
                "basic_salary": 7000000,
                "overtime_rate": 0,
            },  # Manager might not get overtime
        ]

        employees = []
        for emp_data in sample_employees_data:
            email = f"employee.{emp_data['email_suffix']}@gmail.com"
            password = make_password("passwd1234")

            user, created_user = Account.objects.get_or_create(
                email=email,
                defaults={"password": password, "is_staff": False, "is_superuser": False},
            )
            if created_user:
                self.stdout.write(f"Created Account: {email}")

            employee, created_emp = Employee.objects.get_or_create(
                user=user,
                defaults={
                    "name": emp_data["name"],
                    "position": emp_data["position"],
                    "department": emp_data["department"],
                    "contact_number": f"02012345{random.randint(100,999)}",
                    "bank_account_num": f"ACC{random.randint(10000,99999)}",
                    "status": "active",
                    "employment_date": timezone.now().date()
                    - timedelta(days=random.randint(30, 365 * 2)),
                },
            )
            if created_emp:
                self.stdout.write(f"Created Employee: {employee.name}")
            employees.append(employee)

            structure, created_struct = SalaryStructure.objects.get_or_create(
                employee=employee,
                defaults={
                    "basic_salary": Decimal(emp_data["basic_salary"]),
                    "overtime_rate": Decimal(emp_data["overtime_rate"]),
                    "bonus_percentage": Decimal(random.uniform(0, 0.1)),  # 0 to 10% bonus potential
                },
            )
            if created_struct:
                self.stdout.write(f"Created Salary Structure for {employee.name}")

        self.stdout.write(
            "Generating attendance, deductions, bonuses, and salary calculations for the past 3 months..."
        )

        today = timezone.now().date()
        for i in range(3, -1, -1):  # Last 3 months + current month (for generation testing)
            # Target month: first day of the month
            if today.month - i <= 0:
                month = today.month - i + 12
                year = today.year - 1
            else:
                month = today.month - i
                year = today.year

            if month == 0:  # Adjust if month becomes 0
                month = 12
                year -= 1

            # Ensure month is valid
            if not (1 <= month <= 12):
                self.stdout.write(
                    self.style.WARNING(f"Skipping invalid month calculation: {month}/{year}")
                )
                continue

            target_month_date = timezone.datetime(year, month, 1).date()
            num_days_in_month = (
                target_month_date.replace(month=target_month_date.month % 12 + 1, day=1)
                - timedelta(days=1)
            ).day

            for emp in employees:
                self.stdout.write(
                    f"Processing data for {emp.name} for {target_month_date.strftime('%B %Y')}"
                )
                salary_structure = SalaryStructure.objects.get(employee=emp)

                # --- Generate Attendance ---
                total_hours_worked_month = Decimal(0)
                total_overtime_hours_month = Decimal(0)

                # Skip attendance generation for future months
                if target_month_date.year > today.year or (
                    target_month_date.year == today.year and target_month_date.month > today.month
                ):
                    self.stdout.write(
                        f"Skipping attendance for future month: {target_month_date.strftime('%B %Y')} for {emp.name}"
                    )
                else:
                    for day_num in range(1, num_days_in_month + 1):
                        # Skip if the day is in the future for the current month
                        current_day_date = timezone.datetime(year, month, day_num).date()
                        if current_day_date > today:
                            continue

                        if random.random() > 0.1:  # 90% chance of being present
                            hours_worked = Decimal(random.uniform(7.5, 8.5))
                            overtime_hours = Decimal(0)
                            if random.random() > 0.7:  # 30% chance of overtime
                                overtime_hours = Decimal(random.uniform(0.5, 2.5))

                            Attendance.objects.get_or_create(
                                employee=emp,
                                date=current_day_date,
                                defaults={
                                    "shift": random.choice(["Morning", "Afternoon"]),
                                    "hours_worked": hours_worked,
                                    "overtime_hours": overtime_hours,
                                    "is_present": True,
                                    "scan_in_time": timezone.make_aware(
                                        timezone.datetime(
                                            year, month, day_num, 8, random.randint(0, 30)
                                        )
                                    ),
                                    "scan_out_time": timezone.make_aware(
                                        timezone.datetime(
                                            year, month, day_num, 16, random.randint(30, 59)
                                        )
                                    )
                                    + timedelta(hours=float(overtime_hours)),
                                },
                            )
                            total_hours_worked_month += hours_worked
                            total_overtime_hours_month += overtime_hours
                        else:  # Absent
                            Attendance.objects.get_or_create(
                                employee=emp,
                                date=current_day_date,
                                defaults={
                                    "shift": "Absent",
                                    "hours_worked": 0,
                                    "overtime_hours": 0,
                                    "is_present": False,
                                },
                            )

                # --- Generate Deductions (optional) ---
                total_deductions_month = Decimal(0)
                if random.random() > 0.6:  # 40% chance of having a deduction
                    deduction_amount = random.randint(50000, 200000)
                    Deductions.objects.create(
                        employee=emp,
                        date=target_month_date.replace(day=random.randint(5, 20)),
                        reason=random.choice(["Late Penalty", "Unpaid Leave", "Loan Repayment"]),
                        amount=deduction_amount,
                    )
                    total_deductions_month = deduction_amount

                # --- Generate Bonuses (optional) ---
                total_bonuses_month = Decimal(0)
                if random.random() > 0.5:  # 50% chance of having a bonus
                    bonus_amount = random.randint(100000, 500000)
                    Bonuses.objects.create(
                        employee=emp,
                        date=target_month_date.replace(day=random.randint(1, 15)),
                        reason=random.choice(
                            ["Performance Bonus", "Holiday Bonus", "Project Completion"]
                        ),
                        amount=bonus_amount,
                    )
                    total_bonuses_month = bonus_amount

                # --- Calculate and Create SalaryCalculation ---
                # Skip salary calculation for current/future months if no attendance (as it's for past data)
                # The UI generation should handle current month.
                if i == 0 and (
                    target_month_date.year > today.year
                    or (
                        target_month_date.year == today.year
                        and target_month_date.month >= today.month
                    )
                ):
                    self.stdout.write(
                        f"Skipping SalaryCalculation for current/future month {target_month_date.strftime('%B %Y')} for {emp.name} in seeder. Use UI to generate."
                    )
                    continue

                gross_salary = (
                    salary_structure.basic_salary
                    + (total_overtime_hours_month * salary_structure.overtime_rate)
                    + total_bonuses_month
                )
                net_salary = gross_salary - total_deductions_month

                status = "PENDING"
                payment_method = None
                paid_at = None
                if random.random() > 0.3:  # 70% chance of being paid for past months
                    status = "PAID"
                    payment_method = random.choice(SalaryCalculations.PAYMENT_METHOD_CHOICES)[0]
                    paid_at = timezone.make_aware(
                        timezone.datetime(
                            year,
                            month,
                            random.randint(25, num_days_in_month),
                            random.randint(9, 17),
                        )
                    )
                    # Ensure paid_at is not in the future
                    if paid_at > timezone.now():
                        paid_at = timezone.now() - timedelta(days=1)

                SalaryCalculations.objects.update_or_create(
                    employee=emp,
                    month_year=target_month_date,
                    defaults={
                        "basic_salary_snapshot": salary_structure.basic_salary,
                        "overtime_rate_snapshot": salary_structure.overtime_rate,
                        "total_hours_worked": total_hours_worked_month,
                        "total_overtime_hours": total_overtime_hours_month,
                        "total_deductions_amount": total_deductions_month,
                        "total_bonuses_amount": total_bonuses_month,
                        "gross_salary": gross_salary,
                        "net_salary": net_salary,
                        "status": status,
                        "payment_method": payment_method,
                        "paid_at": paid_at,
                        "generated_at": timezone.now()
                        - timedelta(days=i * 30 + random.randint(1, 5)),  # Simulate past generation
                        "notes": "Seeded data." if status == "PAID" else "Pending seeded data.",
                    },
                )
                self.stdout.write(
                    f"Created/Updated SalaryCalculation for {emp.name} for {target_month_date.strftime('%B %Y')} with status {status}"
                )

        self.stdout.write(self.style.SUCCESS("Successfully seeded salary calculation data!"))
