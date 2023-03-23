from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from employee.models import Employee,Bank
from payroll.models import SalaryAdvance
from payroll.views import get_final_salary_details

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

        today = datetime.now()
        current_month = today.month
        months = []
        i = 0
        while (i < 6):
            date = today - relativedelta(months=+i)
            months.append([date.month,date.strftime("%b")])
            i +=1
        months.reverse()
# Getting Salary Advance Data
        monthly_salary_advance_record = []
        for month in months:
            total_salary_advance = 0
            salary_advances = SalaryAdvance.objects.filter(date__month = month[0],status=True).values()
            salary_advances_list = list(salary_advances)
            for salary_advance in salary_advances_list:
                total_salary_advance  = total_salary_advance + salary_advance["amount"]
            monthly_salary_advance_record.append([month[0],month[1],total_salary_advance])
# Getting Net Salary Payed
        monthly_net_salary_payed_record = []
        employees = Employee.objects.filter(emp_type=0,active_status=True).values()
        employees_list = list(employees)
        for month in months:
            response_list = []
            total_net_salary = 0
            for employee in employees_list:
                try:
                        response = get_final_salary_details(emp_id=employee["emp_id"],month=month[0])
                except ValueError:
                    response = "error"
                response_list.append(response)
            for response in response_list:
                if response == "employee_finance_details_error":
                    pass
                elif response == "error":
                    pass
                else:
                    if response[14] == 0:
                        pass
                    else:
                        total_net_salary = total_net_salary + response[12]
            monthly_net_salary_payed_record.append([month[0],month[1],total_net_salary])
            print(monthly_net_salary_payed_record)
        
        return JsonResponse({'monthly_salary_advance_record':monthly_salary_advance_record,'monthly_net_salary_payed_record':monthly_net_salary_payed_record})
    

def add_data():
        banks = [
        ["7010","Bank of Ceylon"],
        ["7038","Standard Chartered Bank"],
        ["7047","Citi Bank"],
        ["7056","Commercial Bank PLC"],
        ["7074","Habib Bank Ltd"],
        ["7083","Hatton National Bank PLC"],
        ["7092","Hongkong Shanghai Bank"],
        ["7108","Indian Bank"],
        ["7117","Indian Overseas Bank"],
        ["7135","Peoples Bank"],
        ["7144","State Bank of India"],
        ["7162","Nations Trust Bank PLC"],
        ["7205","Deutsche Bank"],
        ["7214","National Development Bank PLC"],
        ["7269","MCB Bank Ltd"],
        ["7278","Sampath Bank PLC"],
        ["7287","Seylan Bank PLC"],
        ["7296","Public Bank"],
        ["7302","Union Bank of Colombo PLC"],
        ["7311","Pan Asia Banking Corporation PLC"],
        ["7384","ICICI Bank Ltd"],
        ["7454","DFCC Bank PLC"],
        ["7463","Amana Bank PLC"],
        ["7472","Axis Bank"],
        ["7481","Cargills Bank Limited"],
        ["7719","National Savings Bank"],
        ["7728","Sanasa Development Bank"],
        ["7737","HDFC Bank"],
        ["7746","Citizen Development Business Finance PLC"],
        ["7755","Regional Development Bank"],
        ["7764","State Mortgage & Investment Bank"],
        ["7773","LB Finance PLC"],
        ["7782","Senkadagala Finance PLC"],
        ["7807","Commercial Leasing and Finance"],
        ["7816","Vallibel Finance PLC"],
        ["7825","Central Finance PLC"],
        ["7834","Kanrich Finance Limited"],
        ["7852","Alliance Finance Company PLC"],
        ["7861","LOLC Finance PLC"],
        ["7870","Commercial Credit & Finance PLC"],
        ["7898","Merchant Bank of Sri Lanka & Finance PLC"],
        ["7904","HNB Grameen Finance Limited"],
        ["7913","Mercantile Investment and Finance PLC"],
        ["7922","People's Leasing & Finance PLC"],
        ["8004","Central Bank of Sri Lanka "]
        ]
        

        for bank in banks:
            bankk = Bank(bank[0],bank[1])
            bankk.save()
            print(bank[0])
        print("done")