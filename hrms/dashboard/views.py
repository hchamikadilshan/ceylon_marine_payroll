from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from employee.models import Employee,Bank
from payroll.models import SalaryAdvance
from payroll.views import get_final_salary_details,get_process_salary,calculate_salary

from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.http import JsonResponse

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
    def get(self,request):
        print("inside")
        today = datetime.now()
        current_month = today.month
        months = []
        i = 0
        while (i < 3):
            date = today - relativedelta(months=+i)
            months.append([date.month,date.strftime("%b")])
            i +=1
        months.reverse()
# Getting Salary Advance Data
        # monthly_salary_advance_record = []
        # for month in months:
        #     total_salary_advance = 0
        #     salary_advances = SalaryAdvance.objects.filter(date__month = month[0],status=True).values()
        #     salary_advances_list = list(salary_advances)
        #     for salary_advance in salary_advances_list:
        #         total_salary_advance  = total_salary_advance + salary_advance["amount"]
        #     monthly_salary_advance_record.append([month[0],month[1],total_salary_advance])
# Getting Net Salary Payed
        monthly_net_salary_payed_record = []
        # employees = Employee.objects.filter(emp_type=0,active_status=True).values()
        # employees_list = list(employees)
        # for month in months:
        #     response_list = []
        #     total_net_salary = 0
        #     for employee in employees_list:
        #         try:
        #                 response = get_final_salary_details(emp_id=employee["emp_id"],month=month[0])
        #         except ValueError:
        #             response = "error"
        #         response_list.append(response)
        #     for response in response_list:
        #         if response == "employee_finance_details_error":
        #             pass
        #         elif response == "error":
        #             pass
        #         else:
        #             if response[14] == 0:
        #                 pass
        #             else:
        #                 total_net_salary = total_net_salary + response[12]
        #     monthly_net_salary_payed_record.append([month[0],month[1],total_net_salary])
        #     print(monthly_net_salary_payed_record)

        
        for month in months:
            print("inside calculation")
            response_list = []
            total_net_salary = 0
            employee_data = get_process_salary("multiple",month[0])
            for employee in employee_data:
                try :
                    response = calculate_salary(employee[0],employee[1],employee[2],month[0])
                    if response == "employee_finance_details_error":
                        pass
                    elif response == "Department Empty":
                        pass
                    elif response[-1] == 0:
                        pass
                    else:
                        total_net_salary = total_net_salary + response[12]
                    
                except (ValueError,IndexError):
                    pass
            monthly_net_salary_payed_record.append([month[0],month[1],total_net_salary])
            print(monthly_net_salary_payed_record)
        
        return JsonResponse({'monthly_net_salary_payed_record':monthly_net_salary_payed_record})
    

