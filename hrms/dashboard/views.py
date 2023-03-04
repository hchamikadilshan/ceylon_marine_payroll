from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from employee.models import Employee

# Create your views here.

class DashboardMainView(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def get(self,request):
# Total Employee Count
        employee_record = Employee.objects.filter(active_status=True)
        employee_record_list = list(employee_record)
        active_employees = len(employee_record_list)
# Total Salary 


        return render (request,"dashboard.html",context={'no_of_employees':active_employees})