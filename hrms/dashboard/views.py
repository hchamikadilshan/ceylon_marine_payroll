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
        if today.day > 10:
            i = 1
            while (i < 7):
                date = today - relativedelta(months=+i)
                months.append([date.month,date.strftime("%b")])
                i +=1
        else:
            i = 2
            while (i < 8):
                date = today - relativedelta(months=+i)
                months.append([date.month,date.strftime("%b")])
                i +=1
        months.reverse()

        monthly_net_salary_payed_record = []
        employees = Employee.objects.filter(emp_type=0)
        employees_list = list(employees)
        for month in months:
            response_list = []
            total_net_salary = 0
            employees_count = 0
            # employee_data = get_process_salary("multiple",month[0])
            # for employee in employee_data:
            #     try :
            #         response = calculate_salary(employee[0],employee[1],employee[2],employee[3],employee[4],month[0])
            #         if response == "employee_finance_details_error":
            #             pass
            #         elif response == "Department Empty":
            #             pass
            #         elif response[-1] == 0:
            #             pass
            #         else:
            #             total_net_salary = total_net_salary + response[12]
            #             employees += 1
                    
            #     except (ValueError,IndexError):
            #         pass
            # monthly_net_salary_payed_record.append([month[0],month[1],total_net_salary,employees])
            total_net_salary = 0
            total_salary_advance = 0
            total_epf = 0
            total_allowance = 0
            count = 0
            for employee in employees_list:
                emp_id = employee.emp_id
                try :
                    # print(month[0])
                    response = get_final_salary_details(emp_id=emp_id,month=month[0])
                    net_salary = "{:>9,.2f}".format(response[12])
                    if response == "employee_finance_details_error":
                        # print(f"Found {emp_id} out in employee_finance_details_error")
                        pass
                    elif response == "Department Empty":
                        # print(f"Found {emp_id} out in Department Empty error")
                        pass
                    elif response[-1] == 0:
                        if emp_id == "A01921":
                            print(f"Found {emp_id} out in days 0 {response}")
                        pass
                    elif (employee.bank == None or employee.branch == None or employee.bank_acc_no == "" or employee.bank_acc_name == "" ):
                        # print(f"Found {emp_id} out in bank details ")
                        pass
                    else:    
                        count += 1
                        # print(emp_id,month)
                        total_net_salary += response[12]
                        total_salary_advance  += response[6]
                        total_epf += response[5]
                        total_allowance += response[7]
                        employees_count += 1
                except (ValueError,IndexError):
                    pass
            print(f"No of employees{count}")
            monthly_net_salary_payed_record.append([month[0],month[1],total_net_salary,employees_count,total_salary_advance,total_epf,total_allowance])
        last_month_total = monthly_net_salary_payed_record[5][2]
        last_month_total_formatted = "Rs. {:>9,.2f}".format(last_month_total)
        last_month_salary_advance = monthly_net_salary_payed_record[5][4]
        last_month_salary_advance_formated =  "Rs. {:>9,.2f}".format(last_month_salary_advance)
        last_month_allowance = monthly_net_salary_payed_record[5][6]
        last_month_allowance_formated =  "Rs. {:>9,.2f}".format(last_month_allowance)
        last_month_epf = monthly_net_salary_payed_record[5][5]
        last_month_epf_formated =  "Rs. {:>9,.2f}".format(last_month_epf)

        
        
        
        return JsonResponse({'monthly_net_salary_payed_record':monthly_net_salary_payed_record,"last_month_salary":last_month_total_formatted,"last_month_salary_advance":last_month_salary_advance_formated,"last_month_allowance":last_month_allowance_formated,"last_month_epf":last_month_epf_formated})
    

