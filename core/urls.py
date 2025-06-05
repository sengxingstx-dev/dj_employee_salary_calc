from django.conf.urls import handler404
from django.urls import include, path

from . import views as core_views

handler404 = core_views.custom_404_view

urlpatterns = [
    path("", core_views.home, name="home"),
    path("about/", core_views.about, name="about"),
    path("contact/", core_views.contact, name="contact"),
    path("scan-in/", core_views.scan_in, name="scan-in"),
    path("scan-out/", core_views.scan_out, name="scan-out"),
    # Dashboard
    path("dashboard/", core_views.dashboard, name="dashboard"),
    # Users
    path("accounts/", include("accounts.urls")),
    path("dashboard/profile", core_views.manage_profile, name="manage-profile"),
    path("dashboard/manage-users/", core_views.manage_users, name="manage-users"),
    path("dashboard/manage-users/delete/<int:pk>/", core_views.delete_user, name="delete-user"),
    # Employees
    path("dashboard/manage-employees/", core_views.manage_employees, name="manage-employees"),
    path(
        "dashboard/manage-employees/edit/<int:pk>/", core_views.edit_employee, name="edit-employee"
    ),
    path(
        "dashboard/manage-employees/delete/<int:pk>/",
        core_views.delete_employee,
        name="delete-employee",
    ),
    # Salary structure
    path(
        "dashboard/manage-salary-structures/",
        core_views.manage_salary_structures,
        name="manage-salary-structures",
    ),
    path(
        "dashboard/manage-salary-structures/<int:pk>/update/",
        core_views.edit_salary_structure,
        name="edit-salary-structure",
    ),
    path(
        "dashboard/manage-salary-structures/<int:pk>/delete/",
        core_views.delete_salary_structure,
        name="delete-salary-structure",
    ),
    # Deductions
    path(
        "dashboard/manage-deductions/",
        core_views.manage_deductions,
        name="manage-deductions",
    ),
    path(
        "dashboard/manage-deductions/<int:pk>/update/",
        core_views.edit_deduction,
        name="edit-deduction",
    ),
    path(
        "dashboard/manage-deductions/<int:pk>/delete/",
        core_views.delete_deduction,
        name="delete-deduction",
    ),
    # Bonuses
    path(
        "dashboard/manage-bonuses/",
        core_views.manage_bonuses,
        name="manage-bonuses",
    ),
    path(
        "dashboard/manage-bonuses/<int:pk>/update/",
        core_views.edit_bonus,
        name="edit-bonus",
    ),
    path(
        "dashboard/manage-bonuses/<int:pk>/delete/",
        core_views.delete_bonus,
        name="delete-bonus",
    ),
    #
    path("dashboard/manage-products/", core_views.manage_products, name="manage-products"),
    # NOTE: Attendance
    path("dashboard/manage-attendance/", core_views.manage_attendance, name="manage-attendance"),
    # NOTE: Salary Calculations
    path(
        "dashboard/manage-salary-calculations/",
        core_views.manage_salary_calculations,
        name="manage-salary-calculations",
    ),
    path(
        "dashboard/manage-salary-calculations/<int:pk>/edit/",
        core_views.edit_salary_calculation,
        name="edit-salary-calculation",
    ),
    path(
        "dashboard/manage-salary-calculations/<int:pk>/delete/",
        core_views.delete_salary_calculation,
        name="delete-salary-calculation",
    ),
    # NOTE: Export to excel
    path(
        "dashboard/manage-employees/export-excel/",
        core_views.export_employees_to_excel,
        name="export-employees-excel",
    ),
    path(
        "dashboard/manage-salary-structures/export-excel/",
        core_views.export_salary_structures_to_excel,
        name="export-salary-structures-excel",
    ),
    path(
        "dashboard/manage-deductions/export-excel/",
        core_views.export_deductions_to_excel,
        name="export-deductions-excel",
    ),
    path(
        "dashboard/manage-bonuses/export-excel/",
        core_views.export_bonuses_to_excel,
        name="export-bonuses-excel",
    ),
    path(
        "dashboard/manage-attendance/export-excel/",
        core_views.export_attendance_to_excel,
        name="export-attendance-excel",
    ),
    path(
        "dashboard/manage-salary-calculations/export-excel/",
        core_views.export_salary_calculations_to_excel,
        name="export-salary-calculations-excel",
    ),
]
