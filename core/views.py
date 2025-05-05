from datetime import time

import openpyxl
import pytz
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from openpyxl.styles import Alignment, Font

from accounts.models import Account, Employee
from core.models import Attendance, Bonuses, Deductions, SalaryStructure

from .forms import BonusesForm, DeductionsForm, EmployeeForm, SalaryStructureForm


def custom_404_view(request, exception):
    return render(request, "404.html", status=404)


def home(request):
    employee = None

    if request.user.is_authenticated:
        user = request.user
        employee = get_object_or_404(Employee, user=user)

    context = {"employee": employee}
    return render(request, "core/clients/pages/home.html", context)


def about(request):
    return render(request, "core/clients/pages/about.html")


def contact(request):
    return render(request, "core/clients/pages/contact.html")


@login_required
def scan_in(request):
    if request.method == "POST":
        user = request.user
        employee = get_object_or_404(Employee, user=user)

        # Set the timezone to Asia/Vientiane
        tz = pytz.timezone("Asia/Vientiane")
        now = timezone.now().astimezone(tz)
        today = now.date()
        current_time = now.time()

        # Define shift times
        morning_start = time(8, 0)
        afternoon_start = time(12, 0)
        night_start = time(20, 0)
        work_end = time(16, 0)
        # day_end = time(23, 59, 59)

        # Determine shift
        if morning_start <= current_time < afternoon_start:
            shift = "Morning"
        elif afternoon_start <= current_time < night_start:
            shift = "Afternoon"
        else:
            shift = "Night"

        # Check if it's past work hours
        is_overtime = current_time > work_end

        # Create or get attendance record
        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={
                "shift": shift,
                "hours_worked": 0,
                "overtime_hours": 0,
                "is_present": True,
                "scan_in_time": now,
            },
        )

        if not created:
            if attendance.scan_in_time:
                messages.warning(request, "You have already scanned in today.")
            else:
                attendance.scan_in_time = now
                attendance.shift = shift
                attendance.is_present = True
                attendance.save()
                messages.success(request, f"Scan in successful. Shift: {shift}")
        else:
            messages.success(request, f"Scan in successful. Shift: {shift}")

        # If scanning in after work hours, log overtime
        if is_overtime:
            # attendance.overtime_hours = (
            #     now - now.replace(hour=16, minute=0, second=0, microsecond=0)
            # ).total_seconds() / 3600
            # attendance.save()
            messages.info(
                request, "You are scanning in after regular work hours. Overtime will be logged."
            )

        return redirect("home")  # Redirect to an attendance list view

    # return render(request, "core/scan_in.html")
    return render(request, "core/clients/pages/home.html")


@login_required
def scan_out(request):
    if request.method == "POST":
        user = request.user
        employee = get_object_or_404(Employee, user=user)

        # Set the timezone to Asia/Vientiane
        tz = pytz.timezone("Asia/Vientiane")
        now = timezone.now().astimezone(tz)
        today = now.date()

        try:
            attendance = Attendance.objects.get(employee=employee, date=today)

            if not attendance.scan_in_time:
                messages.error(request, "You need to scan in first.")
            elif attendance.scan_out_time:
                messages.warning(request, "You have already scanned out today.")
            else:
                attendance.scan_out_time = now
                attendance.save()
                attendance.calculate_hours_worked()
                messages.success(request, "Scan out successful.")

                # Check if scanning out after work hours and log additional overtime
                work_end = now.replace(hour=16, minute=0, second=0, microsecond=0)
                if now > work_end:
                    additional_overtime = (now - work_end).total_seconds() / 3600
                    attendance.overtime_hours += additional_overtime
                    attendance.save()
                    messages.info(
                        request, f"Additional overtime logged: {additional_overtime:.2f} hours"
                    )

        except Attendance.DoesNotExist:
            messages.error(request, "No attendance record found for today. Please scan in first.")

        # return redirect("attendance_list")  # Redirect to an attendance list view
        return redirect("home")

    # return render(request, "core/scan_out.html")
    return render(request, "core/clients/pages/home.html")


# NOTE: Dashboard section
@login_required
def dashboard(request):
    return render(request, "core/dashboard/pages/dashboard.html")


def manage_profile(request):
    return render(request, "core/dashboard/pages/manage-profile.html")


def manage_users(request):
    query = request.GET.get("search", "")
    users = Account.objects.all().order_by("-date_joined")

    if query:
        # Search across multiple fields
        users = users.filter(Q(email__icontains=query))

    msg = "Are you sure you want to delete this user?"
    context = {
        "users": users,
        "delete_confirm_msg": msg,
    }
    return render(request, "core/dashboard/pages/manage-users.html", context)


def delete_user(request, pk):
    user = Account.objects.get(pk=pk)

    if request.method == "POST":
        user.delete()
        return redirect("manage-users")

    return render(request, "core/dashboard/pages/manage-users.html")


def manage_employees(request):
    # employee = Employee.objects.get(user=request.user)
    query = request.GET.get("search", "")
    employees = Employee.objects.all().order_by("-updated_at")

    if query:
        # Search across multiple fields
        employees = employees.filter(
            Q(name__icontains=query)
            | Q(contact_number__icontains=query)
            | Q(user__email__icontains=query)
        )

    if request.method == "POST":
        form = EmployeeForm(request.POST)
        email = request.POST.get("email")
        password = request.POST.get("password")

        if form.is_valid():
            hashed_password = make_password(password)
            user = Account.objects.create(email=email, password=hashed_password)
            employee = form.save(commit=True)
            employee.user = user
            employee.save()
            user.save()
            messages.success(request, "Employee created successfully.")
        else:
            print("Form is not valid: ", form.errors)

    context = {
        # "employee": employee,
        "employees": employees,
        "delete_confirm_msg": "Are you sure you want to delete this employee?",
    }
    return render(request, "core/dashboard/pages/manage-employees.html", context)


def edit_employee(request, pk):
    # Get the employee to update
    employee = Employee.objects.get(id=pk)
    data = QueryDict(request.body)  # Use QueryDict to parse the request body
    emp_form = EmployeeForm(data, instance=employee)  # Bind the data to the existing instance

    if request.method == "POST":
        if emp_form.is_valid():
            emp_form.save()
            messages.success(request, "Employee updated successfully.")
        else:
            return JsonResponse({"error": emp_form.errors}, status=400)
        return redirect("manage-employees")
    else:
        emp_form = EmployeeForm(data, instance=employee)

    return render(request, "core/dashboard/pages/manage-employees.html")


def delete_employee(request, pk):
    employee = Employee.objects.get(pk=pk)

    if request.method == "POST":
        employee.delete()
        return redirect("manage-employees")

    return render(request, "core/dashboard/pages/manage-employees.html")


def manage_salary_structures(request):
    query = request.GET.get("search", "")
    employees = Employee.objects.all().order_by("-updated_at")
    structures = SalaryStructure.objects.all().order_by("-updated_at")

    if query:
        # Search across multiple fields
        structures = structures.filter(
            Q(basic_salary__icontains=query) | Q(bonus_percentage__icontains=query)
        )

    if request.method == "POST":
        form = SalaryStructureForm(request.POST)

        if form.is_valid():
            structure = form.save(commit=True)
            structure.save()
            messages.success(request, "Salary Structure created successfully.")
        else:
            print("Form is not valid: ", form.errors)

    context = {
        "employees": employees,
        "structures": structures,
        "delete_confirm_msg": "Are you sure you want to delete this salary structure?",
    }
    return render(request, "core/dashboard/pages/manage-salary-structures.html", context)


def edit_salary_structure(request, pk):
    structure = SalaryStructure.objects.get(id=pk)
    data = QueryDict(request.body)
    structure_form = SalaryStructureForm(data, instance=structure)

    if request.method == "POST":
        if structure_form.is_valid():
            structure_form.save()
            messages.success(request, "Salary structure updated successfully.")
        else:
            return JsonResponse({"error": structure_form.errors}, status=400)
        return redirect("manage-salary-structures")
    else:
        structure_form = SalaryStructureForm(data, instance=structure)

    return render(request, "core/dashboard/pages/manage-salary-structures.html")


def delete_salary_structure(request, pk):
    structure = SalaryStructure.objects.get(pk=pk)

    if request.method == "POST":
        structure.delete()
        return redirect("manage-salary-structures")

    return render(request, "core/dashboard/pages/manage-salary-structures.html")


def manage_deductions(request):
    query = request.GET.get("search", "")
    employees = Employee.objects.all().order_by("-updated_at")
    deductions = Deductions.objects.all().order_by("-updated_at")

    if query:
        # Search across multiple fields
        deductions = deductions.filter(Q(date__icontains=query) | Q(amount__icontains=query))

    if request.method == "POST":
        form = DeductionsForm(request.POST)

        if form.is_valid():
            deduction = form.save(commit=True)
            deduction.save()
            messages.success(request, "Deduction created successfully.")
        else:
            print("Form is not valid: ", form.errors)

    context = {
        "employees": employees,
        "deductions": deductions,
        "delete_confirm_msg": "Are you sure you want to delete this deduction?",
    }
    return render(request, "core/dashboard/pages/manage-deductions.html", context)


def edit_deduction(request, pk):
    deduction = Deductions.objects.get(id=pk)
    data = QueryDict(request.body)
    deduction_form = DeductionsForm(data, instance=deduction)

    if request.method == "POST":
        if deduction_form.is_valid():
            deduction_form.save()
            messages.success(request, "Deduction updated successfully.")
        else:
            return JsonResponse({"error": deduction_form.errors}, status=400)
        return redirect("manage-deductions")
    else:
        deduction_form = DeductionsForm(data, instance=deduction)

    return render(request, "core/dashboard/pages/manage-deductions.html")


def delete_deduction(request, pk):
    deduction = Deductions.objects.get(pk=pk)

    if request.method == "POST":
        deduction.delete()
        return redirect("manage-deductions")

    return render(request, "core/dashboard/pages/manage-deductions.html")


def manage_bonuses(request):
    query = request.GET.get("search", "")
    employees = Employee.objects.all().order_by("-updated_at")
    bonuses = Bonuses.objects.all().order_by("-updated_at")

    if query:
        # Search across multiple fields
        bonuses = bonuses.filter(Q(date__icontains=query) | Q(amount__icontains=query))

    if request.method == "POST":
        form = BonusesForm(request.POST)

        if form.is_valid():
            bonus = form.save(commit=True)
            bonus.save()
            messages.success(request, "Deduction created successfully.")
        else:
            print("Form is not valid: ", form.errors)

    context = {
        "employees": employees,
        "bonuses": bonuses,
        "delete_confirm_msg": "Are you sure you want to delete this bonus?",
    }
    return render(request, "core/dashboard/pages/manage-bonuses.html", context)


def edit_bonus(request, pk):
    bonus = Bonuses.objects.get(id=pk)
    data = QueryDict(request.body)
    bonus_form = BonusesForm(data, instance=bonus)

    if request.method == "POST":
        if bonus_form.is_valid():
            bonus_form.save()
            messages.success(request, "Bonus updated successfully.")
        else:
            return JsonResponse({"error": bonus_form.errors}, status=400)
        return redirect("manage-bonuses")
    else:
        bonus_form = BonusesForm(data, instance=bonus)

    return render(request, "core/dashboard/pages/manage-bonuses.html")


def delete_bonus(request, pk):
    bonus = Bonuses.objects.get(pk=pk)

    if request.method == "POST":
        bonus.delete()
        return redirect("manage-bonuses")

    return render(request, "core/dashboard/pages/manage-bonuses.html")


def manage_products(request):
    context = {
        "delete_confirm_msg": "Are you sure you want to delete this product?",
    }
    return render(request, "core/dashboard/pages/manage-products.html", context)


@login_required
def manage_attendance(request):
    query = request.GET.get("search", "")
    # Fetch attendance records, ordering by date descending, then employee name
    # Use select_related to efficiently fetch related employee data
    attendance_list = (
        Attendance.objects.select_related("employee").all().order_by("-date", "employee__name")
    )

    if query:
        # Search across multiple fields: employee name, date (exact match or partial), shift
        attendance_list = attendance_list.filter(
            Q(employee__name__icontains=query)
            | Q(date__icontains=query)  # Allows searching like '2024-07' or '2024-07-26'
            | Q(shift__icontains=query)
        )

    # Pagination (Optional but recommended for large datasets)
    page = request.GET.get("page", 1)
    paginator = Paginator(attendance_list, 10)  # Show 10 records per page
    try:
        attendance_records = paginator.page(page)
    except PageNotAnInteger:
        attendance_records = paginator.page(1)
    except EmptyPage:
        attendance_records = paginator.page(paginator.num_pages)

    context = {
        "attendance_records": attendance_records,
        "search_query": query,  # Pass the query back for display in the search box
        "delete_confirm_msg": "Are you sure you want to delete this attendance record?",
    }
    return render(request, "core/dashboard/pages/manage-attendance.html", context)


# NOTE: Export to excel section
@login_required
def export_employees_to_excel(request):
    """Exports employee data to an Excel file."""

    # Define the response object for the Excel file
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="employees_report.xlsx"'

    # Create an Excel workbook and select the active worksheet
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Employees"

    # Define the header row
    columns = [
        "No.",
        "Name",
        "Email",
        "Position",
        "Department",
        "Contact Number",
        "Bank Account Number",
        "Employment Date",
        "Status",
    ]
    row_num = 1

    # Write the header row to the worksheet
    for col_num, column_title in enumerate(columns, 1):
        cell = worksheet.cell(row=row_num, column=col_num)
        cell.value = column_title
        # Optional: Add some basic styling to the header
        cell.font = openpyxl.styles.Font(bold=True)
        cell.alignment = openpyxl.styles.Alignment(horizontal="center")

    # Get employee data (consider applying search filter if needed, similar to manage_employees)
    # For simplicity, exporting all employees here.
    employees = (
        Employee.objects.select_related("user").all().order_by("name")
    )  # Use select_related for efficiency

    # Write data rows
    for i, emp in enumerate(employees, start=1):
        row_num += 1
        user_email = emp.user.email if emp.user else "N/A"
        user_status = "Online" if emp.user and emp.user.is_active else "Offline"

        row = [
            i,
            emp.name,
            user_email,
            emp.position,
            emp.department,
            emp.contact_number,
            emp.bank_account_num,
            (
                emp.employment_date.strftime("%Y-%m-%d") if emp.employment_date else "N/A"
            ),  # Format date
            user_status,
        ]

        # Write the row to the worksheet
        for col_num, cell_value in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value
            # Optional: Align text columns to the left
            if isinstance(cell_value, str):
                cell.alignment = openpyxl.styles.Alignment(horizontal="left")

    # Optional: Adjust column widths
    for col_letter in ["B", "C", "D", "E", "F", "G", "H"]:  # Adjust letters based on your columns
        worksheet.column_dimensions[col_letter].width = 20
    worksheet.column_dimensions["A"].width = 5  # For No.

    # Save the workbook to the HttpResponse
    workbook.save(response)

    return response


@login_required
def export_attendance_to_excel(request):
    """Exports attendance data to an Excel file."""

    # Define the response object for the Excel file
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="attendance_report.xlsx"'

    # Create an Excel workbook and select the active worksheet
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Attendance Report"

    # Define the header row
    columns = [
        "No.",
        "Employee Name",
        "Date",
        "Shift",
        "Scan In Time",
        "Scan Out Time",
        "Hours Worked",
        "Overtime Hours",
        "Status",
    ]
    row_num = 1

    # Write the header row to the worksheet
    header_font = Font(bold=True)
    center_alignment = Alignment(horizontal="center")
    left_alignment = Alignment(horizontal="left")

    for col_num, column_title in enumerate(columns, 1):
        cell = worksheet.cell(row=row_num, column=col_num)
        cell.value = column_title
        cell.font = header_font
        cell.alignment = center_alignment

    # Get attendance data (consider applying search filter if needed)
    # For simplicity, exporting all attendance here, ordered like the manage page.
    # You could optionally reuse the search logic from manage_attendance if needed.
    attendance_records = (
        Attendance.objects.select_related("employee").all().order_by("-date", "employee__name")
    )

    # Write data rows
    for i, att in enumerate(attendance_records, start=1):
        row_num += 1
        status = "Present" if att.is_present else "Absent"
        # Format times safely, handling None values
        scan_in_str = (
            att.scan_in_time.astimezone(pytz.timezone("Asia/Vientiane")).strftime("%H:%M:%S")
            if att.scan_in_time
            else "--"
        )
        scan_out_str = (
            att.scan_out_time.astimezone(pytz.timezone("Asia/Vientiane")).strftime("%H:%M:%S")
            if att.scan_out_time
            else "--"
        )

        row = [
            i,
            att.employee.name,
            att.date.strftime("%Y-%m-%d"),  # Format date
            att.get_shift_display(),
            scan_in_str,
            scan_out_str,
            f"{att.hours_worked:.2f}" if att.hours_worked is not None else "0.00",  # Format decimal
            (
                f"{att.overtime_hours:.2f}" if att.overtime_hours is not None else "0.00"
            ),  # Format decimal
            status,
        ]

        # Write the row to the worksheet
        for col_num, cell_value in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value
            # Align text left, numbers/times potentially center or right if desired
            if isinstance(cell_value, (int, float)) or col_num in [
                5,
                6,
                7,
                8,
            ]:  # Align numbers/times center
                cell.alignment = center_alignment
            else:
                cell.alignment = left_alignment

    # Optional: Adjust column widths
    worksheet.column_dimensions["A"].width = 5  # No.
    worksheet.column_dimensions["B"].width = 25  # Employee Name
    worksheet.column_dimensions["C"].width = 12  # Date
    worksheet.column_dimensions["D"].width = 15  # Shift
    worksheet.column_dimensions["E"].width = 15  # Scan In
    worksheet.column_dimensions["F"].width = 15  # Scan Out
    worksheet.column_dimensions["G"].width = 15  # Hours Worked
    worksheet.column_dimensions["H"].width = 15  # Overtime
    worksheet.column_dimensions["I"].width = 10  # Status

    # Save the workbook to the HttpResponse
    workbook.save(response)

    return response
