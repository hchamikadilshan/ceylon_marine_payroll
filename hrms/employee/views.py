from django.shortcuts import render, redirect
from django.views.generic import View, ListView
from .forms import EmployeeForm
from .models import Employee, EmployeeFinance
from django.http import JsonResponse
from datetime import datetime
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth.mixins import LoginRequiredMixin
from adminapp.models import Department

# Create your views here.
class EditEmployee(LoginRequiredMixin,View):
    def post(self,request):
        emp_id = request.POST.get('emp_id')
        emp_name = request.POST.get('emp_name',"")
        emp_type = request.POST['emp_type']
        department = request.POST.get('department',"")
        epf_no = request.POST.get('epf_no',"")
        nic_no = request.POST.get('nic_no',"")
        mobile_no = request.POST.get('mobile_no',"")
        email = request.POST.get('email',"")
        address = request.POST.get('address',"")
        bank_name = request.POST.get('bank_name',"")
        bank_branch = request.POST.get('bank_branch',"")
        bank_acc_name = request.POST.get('bank_acc_name',"")
        bank_acc_no = request.POST.get('bank_acc_no',"")

        employee = Employee.objects.get(emp_id=emp_id)
        department = Department.objects.get(id=department)
        employee.name = emp_name
        employee.dprtmnt = department
        employee.epf_no = epf_no
        employee.nic_no= nic_no
        employee.mobile_no = mobile_no
        employee.email = email
        employee.address = address
        employee.emp_type =emp_type
        employee.bank_acc_name = bank_acc_name
        employee.bank_acc_no = bank_acc_no
        employee.bank_name = bank_name
        employee.bank_branch = bank_branch
        employee.save()
        return redirect('employees_main_view')

class AddEmployeeInAttendance(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def post(self,request):
        emp_id = request.POST['emp_id']
        name = request.POST['name']
        
        employee = Employee(emp_id=emp_id, name=name)
        employee.save()
        return JsonResponse({})
class CheckEmployeeAvailability(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def post(self,request):
        print("fdsddddddddddddd")
        emp_id = request.POST['emp_id']
        employee_exists = Employee.objects.filter(emp_id=emp_id).exists()
        if employee_exists == True:
            return JsonResponse({'status':1})
        else:
            return JsonResponse({'status':0})


class AddNewEmployeeView(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def get(self, request):
        user = request.user
        departments = Department.objects.all()
        return render(request, 'add_new_emp.html',context={'user':user,'departments':departments})

    # def post(self, request):
    #     print("Inside employee add post")
    #     emp_form = EmployeeForm(request.POST)
    #     if emp_form.is_valid():
    #         print("Form is valid")
    #         new_emp = emp_form.save()
    #     else:
    #         print(emp_form.errors.as_data())
    #     return redirect("add_new_emp_view")
    def post(self,request):

        emp_id = request.POST.get('emp_id')
        emp_type = request.POST.get('emp_type')
        name = request.POST.get('name')
        department = request.POST.get('department',"")
        epf_no = request.POST.get('epf_no',"")
        nic_no = request.POST.get('nic_no',"")
        appoinment_date = request.POST.get('appoinment_date',"")
        termination_date = request.POST.get('termination_date',"")
        address = request.POST.get('address',"")
        mobile_no = request.POST.get('mobile_no',"")
        email = request.POST.get('email',"")
        bank_name = request.POST.get('bank_name',"")
        bank_branch = request.POST.get('bank_branch',"")
        bank_acc_name = request.POST.get('bank_acc_name',"")
        bank_acc_no = request.POST.get('bank_acc_no',"")
        

        employee = Employee(emp_id=emp_id, name=name, department=department,emp_type=emp_type,
                            epf_no=epf_no, nic_no=nic_no, address=address, mobile_no=mobile_no, email=email, appoinment_date=None if appoinment_date == "" else appoinment_date, termination_date=None if termination_date == "" else termination_date, bank_name=bank_name, bank_branch=bank_branch, bank_acc_name=bank_acc_name, bank_acc_no=bank_acc_no)
        employee.save()

        return redirect("add_new_emp_view")


# class EmployeesMainView(LoginRequiredMixin,ListView):
#     login_url = '/accounts/login'
#     model = Employee
#     template_name = 'employees.html'

#     def get_queryset(self):
#         return Employee.objects.all()
class EmployeesMainView(LoginRequiredMixin,View):
    def get(self,request):
        employee_list = Employee.objects.all()
        departments = Department.objects.all()
        return render(request,'employees.html',context={'employee_list':employee_list,'departments':departments})
    def post(self,request):
        employees = Employee.objects.all().values()
        employees_list = list(employees)
        departments = Department.objects.all()
        return JsonResponse({'employees_list':employees_list,'departments':departments})


class GetEmpNameView(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def post(self, request):
        emp_id = request.POST['name']

        try:
            employee = Employee.objects.get(emp_id=emp_id)
            employee_name = employee.name
        except Employee.DoesNotExist:
            employee_name = "None"
        return JsonResponse({"name": employee_name}, status=200)


class GetEmployeeSalaryDetails(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def post(self, request):
        emp_id = request.POST['name']
        try:
            employee = Employee.objects.get(emp_id=emp_id)
            try:
                employee_finance = EmployeeFinance.objects.filter(employee=employee).order_by('-submit_date').first()
                return JsonResponse({'status': 1, 'daily_payment': employee_finance.daily_payment, 'ot_payment': employee_finance.ot_payment_rate, 'basic_salary': employee_finance.basic_salary, 'br_payment': employee_finance.br_payment, 'room_charge': employee_finance.room_charge, 'staff_welf': employee_finance.staff_welf_contribution})
            except EmployeeFinance.DoesNotExist:
                return JsonResponse({'status': 0})
        except Employee.DoesNotExist:
            return JsonResponse({'status': 0})


class EmployeeSalaryDetailsView(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def get(self, request):
        user = request.user
        return render(request, 'employee_salary.html',context={'user':user})

    def post(self, request):
        emp_id = request.POST["emp_id_salary"]
        epf_type = request.POST["epf_type"]
        daily_payment = request.POST["emp_daily_payment"]
        ot_payment_rate = request.POST["emp_ot_rate"]
        basic_salary = request.POST["emp_basic_salary"]
        br_payment = request.POST["emp_br_payment"]
        epf = request.POST["emp_EPF"]

        # advance_limit = request.POST["emp_advances_limit"]
        room_charge = request.POST["emp_room_charges"]
        staff_welf_contribution = request.POST["emp_staff_welf_contribution"]

        employee = Employee.objects.get(emp_id=emp_id)

        emplyee_finance_record = EmployeeFinance(
            employee=employee, epf_type=epf_type, daily_payment=daily_payment, ot_payment_rate=ot_payment_rate, basic_salary=0 if basic_salary == "" else basic_salary, br_payment=0 if br_payment == "" else br_payment, epf=epf,  room_charge=0 if room_charge == "" else room_charge, staff_welf_contribution=0 if staff_welf_contribution == "" else staff_welf_contribution, submit_date=datetime.now())

        emplyee_finance_record.save()

        return redirect("employee_salary_details_view")
