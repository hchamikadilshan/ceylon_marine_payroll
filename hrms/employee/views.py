from django.shortcuts import render, redirect
from django.views.generic import View, ListView
from .forms import EmployeeForm
from .models import Employee, EmployeeFinance
from django.http import JsonResponse
from datetime import datetime

# Create your views here.


class AddNewEmployeeView(View):
    def get(self, request):
        return render(request, 'add_new_emp.html')

    def post(self, request):
        print("Inside employee add post")
        emp_form = EmployeeForm(request.POST)
        if emp_form.is_valid():
            print("Form is valid")
            new_emp = emp_form.save()
        else:
            print(emp_form.errors.as_data())
        return redirect("add_new_emp_view")


class EmployeesMainView(ListView):
    model = Employee
    template_name = 'employees.html'

    def get_queryset(self):
        return Employee.objects.all()


class GetEmpNameView(View):
    def post(self, request):
        emp_id = request.POST['name']

        try:
            employee = Employee.objects.get(emp_id=emp_id)
            employee_name = employee.name
        except Employee.DoesNotExist:
            employee_name = "None"
        return JsonResponse({"name": employee_name}, status=200)


class GetEmployeeSalaryDetails(View):
    def post(self, request):
        emp_id = request.POST['name']
        try:
            employee = Employee.objects.get(emp_id=emp_id)
            try:
                employee_finance = EmployeeFinance.objects.filter(employee=employee).order_by('-submit_date').first()
                return JsonResponse({'status': 1, 'daily_payment': employee_finance.daily_payment, 'ot_payment': employee_finance.ot_payment_rate, 'fixed_allowance': employee_finance.fixed_allowance, 'leave_payment': employee_finance.leave_payment, 'br_payment': employee_finance.br_payment, 'adavance': employee_finance.advance_limit, 'room_charge': employee_finance.room_charge, 'staff_welf': employee_finance.staff_welf_contribution})
            except EmployeeFinance.DoesNotExist:
                return JsonResponse({'status': 0})
        except Employee.DoesNotExist:
            return JsonResponse({'status': 0})


class EmployeeSalaryDetailsView(View):
    def get(self, request):
        return render(request, 'employee_salary.html')

    def post(self, request):
        emp_id = request.POST["emp_id_salary"]
        daily_payment = request.POST["emp_daily_payment"]
        ot_payment_rate = request.POST["emp_ot_rate"]
        fixed_allowance = request.POST["emp_fixed_allowance"]
        leave_payment = request.POST["emp_leave_payment"]
        br_payment = request.POST["emp_br_payment"]
        epf = request.POST["emp_EPF"]
        # advance_limit = request.POST["emp_advances_limit"]
        room_charge = request.POST["emp_room_charges"]
        staff_welf_contribution = request.POST["emp_staff_welf_contribution"]

        employee = Employee.objects.get(emp_id=emp_id)

        emplyee_finance_record = EmployeeFinance(
            employee=employee, daily_payment=daily_payment, ot_payment_rate=ot_payment_rate, fixed_allowance=0 if fixed_allowance == "" else fixed_allowance, leave_payment=0 if leave_payment == "" else leave_payment, br_payment=0 if br_payment == "" else br_payment, epf=epf,  room_charge=0 if room_charge == "" else room_charge, staff_welf_contribution=0 if staff_welf_contribution == "" else staff_welf_contribution, submit_date=datetime.now())

        emplyee_finance_record.save()

        return redirect("employee_salary_details_view")
