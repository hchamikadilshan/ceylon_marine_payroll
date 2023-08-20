from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from employee.models import Employee,Bank
from payroll.models import SalaryAdvance
from payroll.views import get_final_salary_details,get_process_salary,calculate_salary

from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.utils.decorators import method_decorator

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


class SalarySummaryChartData(LoginRequiredMixin,View):
    login_url = '/accounts/login'

    @method_decorator(cache_page(60*60*12))  # cache for 12 hours
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    def get(self,request):
        today = datetime.now()
        current_month = today.month
        months = []
        i = 0
        while (i < 6):
            date = today - relativedelta(months=+i)
            months.append([date.month,date.strftime("%b")])
            i +=1
        months.reverse()

        monthly_net_salary_payed_record = []
        for month in months:
            response_list = []
            total_net_salary = 0
            employees = 0
            employee_data = get_process_salary("multiple",month[0])
            for employee in employee_data:
                try :
                    response = calculate_salary(employee[0],employee[1],employee[2],employee[3],employee[4],month[0])
                    if response == "employee_finance_details_error":
                        pass
                    elif response == "Department Empty":
                        pass
                    elif response[-1] == 0:
                        pass
                    else:
                        total_net_salary = total_net_salary + response[12]
                        employees += 1
                    
                except (ValueError,IndexError):
                    pass
            monthly_net_salary_payed_record.append([month[0],month[1],total_net_salary,employees])
        
        return JsonResponse({'monthly_net_salary_payed_record':monthly_net_salary_payed_record})
    

