from django.urls import path
from .views import AddNewEmployeeView, EmployeesMainView, GetEmpNameView, EmployeeSalaryDetailsView, GetEmployeeSalaryDetails,EditEmployee,CheckEmployeeAvailability,GetBankBranches,EditEmployeeSalaryDetails


urlpatterns = [
    path('add_new', AddNewEmployeeView.as_view(), name="add_new_emp_view"),
    path('edit_employee', EditEmployee.as_view(), name="edit_employee_view"),
    path('emplopyees', EmployeesMainView.as_view(),name="employees_main_view"),
    path('emplopyee_salary_details', EmployeeSalaryDetailsView.as_view(), name="employee_salary_details_view"),
    path('get_emplopyee_salary_details', GetEmployeeSalaryDetails.as_view(),
         name="get_emplopyee_salary_details_view"),
    path('get_emp_name', GetEmpNameView.as_view(), name="get_emp_name_view"),
    path('check_emp_id_availability', CheckEmployeeAvailability.as_view(), name="check_emp_id_availability"),
    path('get_bank_branches', GetBankBranches.as_view(), name="get_bank_branches"),               
    path('edit_employee_finance', EditEmployeeSalaryDetails.as_view(), name="edit_employee_finance"),               
]
