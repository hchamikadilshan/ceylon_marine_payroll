from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from employee.models import Employee

# Create your views here.

class DashboardMainView(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def get(self,request):
        user = request.user
# Total Employee Count
        normal_employee_record = Employee.objects.filter(active_status=True,emp_type=0)
        normal_employee_record_list = list(normal_employee_record)
        normal_active_employees = len(normal_employee_record_list)

        shift_employee_record = Employee.objects.filter(active_status=True,emp_type=1)
        shift_employee_record_list = list(shift_employee_record)
        shift_active_employees = len(shift_employee_record_list)
# Total Salary 
        return render (request,"dashboard.html",context={'no_of_normal_employees':normal_active_employees,'no_of_shift_employees':shift_active_employees,'user':user})