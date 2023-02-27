from django.urls import path
from .views import AddNewEmployeeView, EmployeesMainView, GetEmpNameView, EmployeeSalaryDetailsView, GetEmployeeSalaryDetails,EditEmployee


urlpatterns = [
    path('add_new', AddNewEmployeeView.as_view(), name="add_new_emp_view"),
    path('edit_employee', EditEmployee.as_view(), name="edit_employee_view"),
    path('emplopyees', EmployeesMainView.as_view(),name="employees_main_view"),
    path('emplopyee_salary_details', EmployeeSalaryDetailsView.as_view(), name="employee_salary_details_view"),
    path('get_emplopyee_salary_details', GetEmployeeSalaryDetails.as_view(),
         name="get_emplopyee_salary_details_view"),
    path('get_emp_name', GetEmpNameView.as_view(), name="get_emp_name_view"),
]
