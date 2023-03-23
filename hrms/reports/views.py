from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from payroll.views import get_final_salary_details
from employee.models import Employee

import io
from reportlab.lib.pagesizes import A4,landscape
from reportlab.platypus import SimpleDocTemplate,Table,TableStyle,Frame
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch,cm

# Create your views here.
class SalarySignatureReport(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def get(self,request):
        user = request.user
        return render(request,'salary_signature_report.html' ,context={'user':user})
    def post(self,request):
        emp_type = request.POST["emp_type"]
        month_year = request.POST["month_year"]
        month_year_split = month_year.split('-')
        response_employees = []
        if emp_type == 2:
            employees = Employee.objects.filter(active_status=True).values()
        else:
            employees = Employee.objects.filter(emp_type=emp_type,active_status=True).values()
        employees_list = list(employees)
        i = 0
        for employee in employees_list:
            try:
                employee_response = get_final_salary_details(emp_id=employee["emp_id"],month=month_year_split[1])
                if employee_response == "employee_finance_details_error":
                    pass
                else:
                    response_employees.append([employee_response[-6],employee_response[-5],f"{employee_response[12]:9.2f}"])
            except (ValueError,IndexError):
                pass
        table_data = []
        document_heading = ['Attendance Report']
        table_data.append(document_heading)
        table_heading = ['Emp ID', 'Name', 'Net Salary','Signature']
        table_data.append(table_heading)
        print(response_employees)
        return 