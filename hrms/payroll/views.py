from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse,FileResponse
from employee.models import Employee, EmployeeFinance
from attendance.models import Attendance
from django.db.models import Avg, Case, Count, F
from datetime import  datetime
from .models import SalaryAdvance,Alllowance

from reportlab.pdfgen import canvas
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Table,TableStyle
from reportlab.lib import colors
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.


class EmployeeSalaryPdfView(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def post(self,request):
        emp_id = request.POST['attendance_view_emp_id']
        year_month = request.POST["attendance_view_month_year"]

        year_month_split = year_month.split('-')
        emp = Employee.objects.get(emp_id=emp_id)
        attendance_record = Attendance.objects.filter(
            employee=emp, date__month=year_month_split[1]).order_by('date').values()
        attendance_record_list = list(attendance_record)
        min_salary_amount = 16600.0
        total_working_hours = 0
        total_ot_hours = 0
        epf = 0
# ----------------------------------------------------------------------------------------
        # Adding Heading Data
        table_data = []
        document_heading_1 = ['Attendance Report']
        document_heading_2 = [""]
        document_heading_3 = ["Emp ID :",emp_id,"Emp Name :","H C D Hapuarachchi"]
        document_heading_4 = ["Month :",emp_id,"Department :","H C D Hapuarachchi"]
        table_heading = ['Date', 'Day', 'In Time',
                         'Out Time', 'Working Hours', 'OT Hours','Remarks']
        table_data.append(document_heading_1)
        table_data.append(document_heading_2)
        table_data.append(document_heading_3)
        table_data.append(document_heading_4)
        table_data.append(table_heading)
# --------------------------------------------------------------------------------------- 
        for record in attendance_record_list:

            normal_working_hours = 9.0
            ot_hours = 0
            date = str(record['date']).split('-')
            in_time = str(record['in_time']).split('.')
            out_time = str(record['out_time']).split('.')
            in_time_obj = datetime(int(date[0]), int(date[1]), int(
                date[2]), int(in_time[0]), int(in_time[1]))
            out_time_obj = datetime(int(date[0]), int(date[1]), int(
                date[2]), int(out_time[0]), int(out_time[1]))
            attendance_in_time = datetime(
                int(date[0]), int(date[1]), int(date[2]), 7, 30)
            attendance_out_time = datetime(
                int(date[0]), int(date[1]), int(date[2]), 16, 30)
            attendance_out_time_noon = datetime(
                int(date[0]), int(date[1]), int(date[2]), 12, 00)
            attendance_out_time_mid_night = datetime(
                int(date[0]), int(date[1]), int(date[2]), 00, 00)

            if record['next_day'] == 0:
                if (in_time_obj == attendance_in_time and out_time_obj == attendance_out_time):
                    pass
                # Deducting the punishment hours
                elif (in_time_obj > attendance_in_time or out_time_obj < attendance_out_time):
                    if in_time_obj > attendance_in_time:
                        in_time_difference = in_time_obj - attendance_in_time
                        in_time_difference_hours = in_time_difference.total_seconds()/(60*60)
                        a = (in_time_difference.total_seconds()/(60*60))//0.5
                        b = (in_time_difference.total_seconds()/(60*60)) % 0.5
                        if in_time_difference_hours <= 0.5:
                            normal_working_hours = normal_working_hours - 0.5
                        elif in_time_difference_hours > 0.5:
                            normal_working_hours = normal_working_hours - \
                                (0.5 * a) - (0.5 if b != 0 else 0)
                    if out_time_obj < attendance_out_time:
                        out_time_difference = attendance_out_time - out_time_obj
                        out_time_difference_hours = out_time_difference.total_seconds()/(60*60)
                        a = (out_time_difference.total_seconds()/(60*60))//0.5
                        b = (out_time_difference.total_seconds()/(60*60)) % 0.5
                        if out_time_difference_hours <= 0.5:
                            normal_working_hours = normal_working_hours - 0.5
                        elif out_time_difference_hours > 0.5:
                            normal_working_hours = normal_working_hours - \
                                (0.5 * a) - (0.5 if b != 0 else 0)
                if ((out_time_obj <= attendance_out_time_noon)):
                    pass
                else:
                    normal_working_hours = normal_working_hours - 1

                # O/T Hours Calculation
                if (in_time_obj < attendance_in_time or out_time_obj > attendance_out_time):
                    if in_time_obj < attendance_in_time:
                        in_time_difference_ot = attendance_in_time - in_time_obj
                        in_time_difference_ot_hours = in_time_difference_ot.total_seconds()/(60*60)
                        a = (in_time_difference_ot.total_seconds()/(60*60))//0.5
                        b = (in_time_difference_ot.total_seconds()/(60*60)) % 0.5
                        if in_time_difference_ot_hours < 0.5:
                            pass
                        elif in_time_difference_ot_hours >= 0.5:
                            ot_hours = ot_hours + (0.5 * a)
                    if out_time_obj > attendance_out_time:
                        out_time_difference_ot = out_time_obj - attendance_out_time
                        out_time_difference_ot_hours = out_time_difference_ot.total_seconds()/(60*60)
                        a = (out_time_difference_ot_hours//0.5)
                        b = (out_time_difference_ot_hours % 0.5)
                        if out_time_difference_ot_hours < 0.5:
                            pass
                        elif out_time_difference_ot_hours > 0.5:
                            ot_hours = ot_hours + (0.5 * a)
                if record['day'] == "Saturday":
                    ot_hours = ot_hours + 3
                elif record['day'] == "Sunday":
                    ot_hours = ot_hours + 4
                elif record['special_holiday'] == 1:
                    ot_hours = ot_hours + 4
            # Next Day Out
            else:

                # Out time O/T Hours Calculation
                if record['day'] == "Saturday":
                    ot_hours = ot_hours + 3
                elif record['day'] == "Sunday":
                    ot_hours = ot_hours + 4
                elif record['special_holiday'] == 1:
                    ot_hours = ot_hours + 4
                ot_hours = ot_hours + 7.5
                out_time_difference_ot_special = out_time_obj - attendance_out_time_mid_night
                out_time_difference_ot_special_hours = out_time_difference_ot_special.total_seconds() / \
                    (60*60)
                a = (out_time_difference_ot_special_hours//0.5)
                b = (out_time_difference_ot_special_hours % 0.5)
                if out_time_difference_ot_special_hours < 0.5:
                    pass
                elif out_time_difference_ot_special_hours >= 0.5:
                    ot_hours = ot_hours + (0.5 * a)
                # In time O/T Hours Calculation
                if (in_time_obj < attendance_in_time):
                    print(record)
                    in_time_difference_ot = attendance_in_time - in_time_obj
                    in_time_difference_ot_hours = in_time_difference_ot.total_seconds()/(60*60)
                    print(in_time_difference_ot_hours)
                    a = (in_time_difference_ot.total_seconds()/(60*60))//0.5
                    b = (in_time_difference_ot.total_seconds()/(60*60)) % 0.5
                    if in_time_difference_ot_hours < 0.5:
                        pass
                    elif in_time_difference_ot_hours >= 0.5:
                        ot_hours = ot_hours + (0.5 * a)
                elif (in_time_obj > attendance_in_time):
                    in_time_difference = in_time_obj - attendance_in_time
                    in_time_difference_hours = in_time_difference.total_seconds()/(60*60)
                    a = (in_time_difference.total_seconds()/(60*60))//0.5
                    b = (in_time_difference.total_seconds()/(60*60)) % 0.5
                    if in_time_difference_hours <= 0.5:
                        normal_working_hours = normal_working_hours - 0.5
                    elif in_time_difference_hours > 0.5:
                        normal_working_hours = normal_working_hours - \
                            (0.5 * a) - (0.5 if b != 0 else 0)
                if in_time_obj < attendance_out_time_noon:
                    normal_working_hours = normal_working_hours - 1
                else:
                    pass
            record['ot_hours'] = ot_hours
            record['working_hours'] = normal_working_hours
# -------------------------------------------------------------------------------------
            # Adding Data to the PDF
            row = []
            row.append(record['date'])
            row.append(record['day'])
            row.append(record['in_time'])
            row.append(record['out_time'])
            row.append(normal_working_hours)
            row.append(ot_hours)
            row.append("")
            table_data.append(row)
# -------------------------------------------------------------------------------------
# Calculating Salary

        for record in attendance_record_list:
            total_working_hours = total_working_hours + record['working_hours']
            total_ot_hours = total_ot_hours + record['ot_hours']
        
        try:
            employee_finance = EmployeeFinance.objects.filter(
                employee=emp).order_by('-submit_date').first()
            if employee_finance is not None:
                daily_payment_rate = employee_finance.daily_payment
                ot_payment_rate = employee_finance.ot_payment_rate
            else:
                return JsonResponse({})
            hourly_payment_rate = daily_payment_rate/8
            
            basic_salary = total_working_hours * hourly_payment_rate
            ot_payment = total_ot_hours * ot_payment_rate

            net_salary = basic_salary + ot_payment

            

# Room Charges
            room_charge = employee_finance.room_charge

            net_salary = basic_salary + ot_payment - room_charge
# Advance Payment Calculation
            try:
                advance_payment_data = SalaryAdvance.objects.filter(
                    employee=emp, date__month=year_month_split[1]).order_by('date').values()
                advance_payment_data_list = list(advance_payment_data)
                total_advance_amount = 0
                for advance in advance_payment_data_list:
                    total_advance_amount = total_advance_amount + \
                        advance["amount"]
                net_salary = net_salary - total_advance_amount

            except SalaryAdvance.DoesNotExist:
                print("Salary Advances does not exists")
# Allowances Calculation
            try:
                allowance_data = Alllowance.objects.filter(
                    employee=emp, date__month=year_month_split[1],status =True).order_by('date').values()
                allowance_data_list = list(allowance_data)
                total_allowance = 0
                for allowance in allowance_data_list:
                    total_allowance = total_allowance + allowance["amount"]
            except Alllowance.DoesNotExist:
                print("No Allowance")
# EPF Calculation
            if employee_finance.epf_type == "1":
                epf = epf + (min_salary_amount * 0.08)
            elif employee_finance.epf_type == "2":
                pass
            net_salary = net_salary - epf + total_allowance

            room_charge = "{:.2f}".format(room_charge)
            epf = "{:.2f}".format(epf)
            total_advance_amount = "{:.2f}".format(total_advance_amount)
            total_allowance = "{:.2f}".format(total_allowance)
            ot_payment = "{:.2f}".format(ot_payment)
            ot_payment_rate = "{:.2f}".format(ot_payment_rate)
            hourly_payment_rate = "{:.2f}".format(hourly_payment_rate)
            basic_salary = "{:.2f}".format(basic_salary)
            net_salary = "{:.2f}".format(net_salary)
        except EmployeeFinance.DoesNotExist:
            print("Employee Finance Does not exists")


# -------------------------------------------------------------------------------------
        empty_row = ["","","","","","",""]
        salary_details_row_1 = [
            "Basic Salary", f"{hourly_payment_rate} x {total_working_hours}", "", basic_salary, ""]
        salary_details_row_2 = [
            "Total OT Payment", f"{ot_payment_rate} x {total_ot_hours}", "", ot_payment, ""]
        salary_details_row_3 = [
            "Allowance", "", "", total_allowance, "", "", ""]
        salary_details_row_4 = [
            "Salary Advance", "", "", f"({total_advance_amount})", "", "", ""]
        salary_details_row_5 = [
            "EPF", "", "", f"({epf})", "", ""]
        salary_details_row_6 = [
            "Room Charge", "", "", f"({room_charge})", "", ""]
        salary_details_row_7 = [
            "Net Payment", "", "", "", "", net_salary]
            
        # table_data.append(empty_row)
        table_data.append(salary_details_row_1)
        table_data.append(salary_details_row_2)
        table_data.append(salary_details_row_3)
        table_data.append(salary_details_row_4)
        table_data.append(salary_details_row_5)
        table_data.append(salary_details_row_6)
        table_data.append(salary_details_row_7)

        buffer = io.BytesIO()
        file_name = f"{emp_id}_{year_month}_Salary_Details.pdf"
        title = f"{emp_id}_{year_month}_Salary_Details"
        pdf = SimpleDocTemplate(buffer,pagesize = A4, title=title)
        elements = []
        attendance_table = Table(table_data)
        # salary_table = Table(salary_data)
        attendance_table_styles = TableStyle(
            [
             ('SPAN', (0, 0), (-1, 0)),
             ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
             ('SPAN', (0, 1), (-1, 1)),
             ('SPAN', (3, 2), (-1, 2)),
             ('SPAN', (3, 3), (-1, 3)),
            #  ('SPAN', (0, -8), (-1, -8)),
             ('SPAN', (1, -7), (2,-7)),# Basic Salary Row
             ('SPAN', (3, -7), (4, -7)),  
             ('SPAN', (5, -7), (6, -7)),
             ('SPAN', (1, -6), (2, -6)),  # OT Row
             ('SPAN', (3, -6), (4, -6)),
             ('SPAN', (5, -6), (6, -6)),
             ('SPAN', (1, -5), (2, -5)),  # Allowance Row
             ('SPAN', (3, -5), (4, -5)), 
             ('SPAN', (5, -5), (6, -5)),
             ('SPAN', (1, -4), (2, -4)),  # Salary Advance Row
             ('SPAN', (3, -4), (4, -4)), 
             ('SPAN', (5, -4), (6, -4)),
             ('SPAN', (1, -3), (2, -3)),  # EPF Row
             ('SPAN', (3, -3), (4, -3)),
             ('SPAN', (5, -3), (6, -3)),
             ('SPAN', (1, -2), (2, -2)),  # Room Charge Row
             ('SPAN', (3, -2), (4, -2)),
             ('SPAN', (5, -2), (6, -2)),
             ('SPAN', (1, -1), (2, -1)),  # Net Payment Row
             ('SPAN', (3, -1), (4, -1)),
             ('SPAN', (5, -1), (6, -1)),
             ('GRID', (0, 2), (-1, 2), 1, colors.black),
             ('GRID', (0, 3), (-1, 3), 1, colors.black),
             ('BOX', (0, 4), (-1, -1), 1, colors.black),
             ('GRID', (0, 4), (-1, -1), 1, colors.black),
             ('ALIGN', (2, 4), (5, -1),'RIGHT'),
             ('FONT', (0, 0), (-1, -1), 'Helvetica',9.5),
             

             ]
            
        )
        # salary_table_styles = TableStyle(
        #     [
        #         ('GRID', (0, 0), (-1, -1), 1, colors.black),
        #     ]
        # )
        attendance_table.setStyle(attendance_table_styles)
        # salary_table.setStyle(salary_table_styles)
        elements.append(attendance_table)
        # elements.append(salary_table)
        pdf.build(elements)
        buffer.seek(0)
        
        return FileResponse(buffer, as_attachment=True, filename=file_name)

class AllowancesView(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def get(self,request):
        return render(request,'allowances.html')

    def post(self,request):
        print("inside allowance payment")
        emp_id = request.POST['emp_id']
        date = request.POST['date']
        amount = request.POST['amount']
        description = request.POST['description']
        emp = Employee.objects.get(emp_id=emp_id)
        time_stamp = datetime.now()

        allowance = Alllowance(
            employee=emp, date=date,description=description, amount=amount, time_stamp=time_stamp)
        allowance.save()
        return  JsonResponse({})


class GetAllowanceData(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def post(self,request):
        emp_id = request.POST['emp_id']
        emp = Employee.objects.get(emp_id=emp_id)
        allowance_data = Alllowance.objects.filter(
            employee=emp).order_by('date').values()
        allowance_data_list = list(allowance_data)
        return JsonResponse({'allowance_data_list': allowance_data_list})
class EditAllowance(LoginRequiredMixin,View):
    def post(self,request):
        emp_id = request.POST['emp_id']
        date = request.POST['date']
        amount = request.POST['amount']
        description = request.POST['description']
        status = request.POST['status']
        id = request.POST["id"]
        emp = Employee.objects.get(emp_id=emp_id)
        time_stamp = datetime.now()

        allowance_record = Alllowance.objects.get(
            employee=emp, id=id)
        allowance_record.date = date
        allowance_record.amount=amount
        allowance_record.description=description
        allowance_record.status= (True if status == "true" else False)
        allowance_record.time_stamp = time_stamp
        allowance_record.save()
        return JsonResponse({})
class GetAdvancePaymentData(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def post(self,request):
        emp_id = request.POST['emp_id']
        emp = Employee.objects.get(emp_id=emp_id)
        advance_payment_data = SalaryAdvance.objects.filter(employee=emp).order_by('date').values()
        advance_payment_data_list = list(advance_payment_data)
        return JsonResponse({'advance_payment_data_list': advance_payment_data_list})

class AdvancePaymentsView(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def get(self, request):
        return render(request, 'advance_payment.html')
    def post(self,request):
        print("inside advance payment")
        emp_id = request.POST['emp_id']
        date = request.POST['date']
        amount = request.POST['amount']
        emp = Employee.objects.get(emp_id=emp_id)
        time_stamp = datetime.now()

        salary_advance = SalaryAdvance(
            employee=emp, date=date, amount=amount, time_stamp=time_stamp)
        salary_advance.save()
        return  JsonResponse({})



class SalaryReportView(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def get(self, request):
        return render(request, 'payroll_test.html')

    def post(self, request):
        emp_id = request.POST['emp_id']
        year_month = request.POST["month"]
        year_month_split = year_month.split('-')
        emp = Employee.objects.get(emp_id=emp_id)
        attendance_record = Attendance.objects.filter(
            employee=emp, date__month=year_month_split[1]).order_by('date').values()
        attendance_record_list = list(attendance_record)
        min_salary_amount = 16600.0
        total_working_hours = 0
        total_ot_hours = 0
        epf = 0

        for record in attendance_record_list:
            normal_working_hours = 9.0
            ot_hours = 0
            date = str(record['date']).split('-')
            in_time = str(record['in_time']).split('.')
            out_time = str(record['out_time']).split('.')
            in_time_obj = datetime(int(date[0]), int(date[1]), int(
                date[2]), int(in_time[0]), int(in_time[1]))
            out_time_obj = datetime(int(date[0]), int(date[1]), int(
                date[2]), int(out_time[0]), int(out_time[1]))
            attendance_in_time = datetime(
                int(date[0]), int(date[1]), int(date[2]), 7, 30)
            attendance_out_time = datetime(
                int(date[0]), int(date[1]), int(date[2]), 16, 30)
            attendance_out_time_noon = datetime(
                int(date[0]), int(date[1]), int(date[2]), 12, 00)
            attendance_out_time_mid_night = datetime(
                int(date[0]), int(date[1]), int(date[2]), 00, 00)

            if record['next_day'] == 0:
                if (in_time_obj == attendance_in_time and out_time_obj == attendance_out_time):
                    pass
# Deducting the punishment hours
                elif (in_time_obj > attendance_in_time or out_time_obj < attendance_out_time):
                    if in_time_obj > attendance_in_time:
                        in_time_difference = in_time_obj - attendance_in_time
                        in_time_difference_hours = in_time_difference.total_seconds()/(60*60)
                        a = (in_time_difference.total_seconds()/(60*60))//0.5
                        b = (in_time_difference.total_seconds()/(60*60)) % 0.5
                        if in_time_difference_hours <= 0.5:
                            normal_working_hours = normal_working_hours - 0.5
                        elif in_time_difference_hours > 0.5:
                            normal_working_hours = normal_working_hours - \
                                (0.5 * a) - (0.5 if b != 0 else 0)
                    if out_time_obj < attendance_out_time:
                        out_time_difference = attendance_out_time - out_time_obj
                        out_time_difference_hours = out_time_difference.total_seconds()/(60*60)
                        a = (out_time_difference.total_seconds()/(60*60))//0.5
                        b = (out_time_difference.total_seconds()/(60*60)) % 0.5
                        if out_time_difference_hours <= 0.5:
                            normal_working_hours = normal_working_hours - 0.5
                        elif out_time_difference_hours > 0.5:
                            normal_working_hours = normal_working_hours - \
                                (0.5 * a) - (0.5 if b != 0 else 0)
                if ((out_time_obj <= attendance_out_time_noon)):
                    pass
                else:
                    normal_working_hours = normal_working_hours - 1
                
# O/T Hours Calculation
                if (in_time_obj < attendance_in_time or out_time_obj > attendance_out_time):
                    if in_time_obj < attendance_in_time :
                        in_time_difference_ot = attendance_in_time - in_time_obj
                        in_time_difference_ot_hours = in_time_difference_ot.total_seconds()/(60*60)
                        a = (in_time_difference_ot.total_seconds()/(60*60))//0.5
                        b = (in_time_difference_ot.total_seconds()/(60*60)) % 0.5
                        if in_time_difference_ot_hours < 0.5:
                            pass
                        elif in_time_difference_ot_hours >= 0.5:
                            ot_hours = ot_hours + (0.5 * a) 
                    if out_time_obj > attendance_out_time:
                        out_time_difference_ot = out_time_obj - attendance_out_time
                        out_time_difference_ot_hours = out_time_difference_ot.total_seconds()/(60*60)
                        a = (out_time_difference_ot_hours//0.5)
                        b = (out_time_difference_ot_hours % 0.5)
                        if out_time_difference_ot_hours < 0.5:
                            pass
                        elif out_time_difference_ot_hours >= 0.5:
                            ot_hours = ot_hours + (0.5 * a) 
                if (record['day'] == "Saturday" and (in_time_obj <= attendance_in_time and out_time_obj >= attendance_out_time)):
                    ot_hours = ot_hours + 3
                elif (record['day'] == "Sunday" and (in_time_obj <= attendance_in_time and out_time_obj >= attendance_out_time)):
                    ot_hours = ot_hours + 4
                elif (record['special_holiday'] == 1 and (in_time_obj <= attendance_in_time and out_time_obj >= attendance_out_time)):
                    ot_hours = ot_hours + 4
# Next Day Out
            else: 
                
# Out time O/T Hours Calculation
                if (record['day'] == "Saturday" ):
                    ot_hours = ot_hours + 3
                elif (record['day'] == "Sunday" ):
                    ot_hours = ot_hours + 4
                elif (record['special_holiday'] == 1 ):
                    ot_hours = ot_hours + 4
                ot_hours = ot_hours +7.5
                out_time_difference_ot_special = out_time_obj - attendance_out_time_mid_night
                out_time_difference_ot_special_hours = out_time_difference_ot_special.total_seconds() / (60*60)
                a = (out_time_difference_ot_special_hours//0.5)
                b = (out_time_difference_ot_special_hours % 0.5)
                if out_time_difference_ot_special_hours < 0.5:
                        pass
                elif out_time_difference_ot_special_hours >= 0.5:
                    ot_hours = ot_hours + (0.5 * a) 
# In time O/T Hours Calculation
                if (in_time_obj < attendance_in_time):
                    in_time_difference_ot = attendance_in_time - in_time_obj
                    in_time_difference_ot_hours = in_time_difference_ot.total_seconds()/(60*60)
                    a = (in_time_difference_ot.total_seconds()/(60*60))//0.5
                    b = (in_time_difference_ot.total_seconds()/(60*60)) % 0.5
                    if in_time_difference_ot_hours < 0.5:
                        pass
                    elif in_time_difference_ot_hours >= 0.5:
                        ot_hours = ot_hours + (0.5 * a)
                elif (in_time_obj > attendance_in_time ):
                    in_time_difference = in_time_obj - attendance_in_time
                    in_time_difference_hours = in_time_difference.total_seconds()/(60*60)
                    a = (in_time_difference.total_seconds()/(60*60))//0.5
                    b = (in_time_difference.total_seconds()/(60*60)) % 0.5
                    if in_time_difference_hours <= 0.5:
                        normal_working_hours = normal_working_hours - 0.5
                    elif in_time_difference_hours > 0.5:
                        normal_working_hours = normal_working_hours - (0.5 * a) - (0.5 if b != 0 else 0)
                if in_time_obj < attendance_out_time_noon:
                    normal_working_hours = normal_working_hours - 1
                else:
                    pass
            record['ot_hours'] = ot_hours
            record['working_hours'] = normal_working_hours
            # total_working_hours = total_working_hours + normal_working_hours
            # total_ot_hours = total_ot_hours + ot_hours
        for record in attendance_record_list:
            total_working_hours = total_working_hours + record['working_hours']
            total_ot_hours = total_ot_hours + record['ot_hours']
# Advance Payment Calculation
        try:
            employee_finance = EmployeeFinance.objects.filter(
                employee=emp).order_by('-submit_date').first()
            if employee_finance is not None:
                daily_payment_rate = employee_finance.daily_payment
                ot_payment_rate = employee_finance.ot_payment_rate
                room_charge = employee_finance.room_charge
            else:
                return JsonResponse({'error':"no employee finance data"})
            # daily_payment_rate = employee_finance.daily_payment
            hourly_payment_rate = daily_payment_rate/8
            # ot_payment_rate = employee_finance.ot_payment_rate
            basic_salary = total_working_hours * hourly_payment_rate
            ot_payment = total_ot_hours * ot_payment_rate

# Room Charges
            
            net_salary = basic_salary + ot_payment - room_charge
            try:
                advance_payment_data = SalaryAdvance.objects.filter(
                    employee=emp, date__month=year_month_split[1]).order_by('date').values()
                advance_payment_data_list = list(advance_payment_data)
                total_advance_amount = 0
                for advance in advance_payment_data_list:
                    total_advance_amount = total_advance_amount + advance["amount"]
                net_salary = net_salary - total_advance_amount

            except SalaryAdvance.DoesNotExist:
                print("Salary Advances does not exists")
# Allowances Calculation 
            try:
                allowance_data = Alllowance.objects.filter(
                    employee=emp, date__month=year_month_split[1],status =True).order_by('date').values()
                allowance_data_list = list(allowance_data)
                total_allowance = 0
                for allowance in allowance_data_list:
                    total_allowance = total_allowance + allowance["amount"]
            except Alllowance.DoesNotExist:
                print("No Allowance")



# EPF Calculation
            if employee_finance.epf_type == "1":
                epf = epf + (min_salary_amount * 0.08)
            elif employee_finance.epf_type == "2":
                pass
            net_salary = net_salary - epf + total_allowance

            room_charge = "{:.2f}".format(room_charge)
            epf = "{:.2f}".format(epf)
            total_advance_amount = "{:.2f}".format(total_advance_amount)
            total_allowance = "{:.2f}".format(total_allowance)
            ot_payment = "{:.2f}".format(ot_payment)
            ot_payment_rate = "{:.2f}".format(ot_payment_rate)
            hourly_payment_rate = "{:.2f}".format(hourly_payment_rate)
            basic_salary = "{:.2f}".format(basic_salary)
            net_salary = "{:.2f}".format(net_salary)
        except EmployeeFinance.DoesNotExist:
            print("Employee Finance Does not exists")

        return JsonResponse({'attendance_list': attendance_record_list, 'total_working_hours': total_working_hours, 'total_ot_hours': total_ot_hours, 'basic_salary': basic_salary, 'ot_payment': ot_payment, 'hourly_payment_rate': hourly_payment_rate, 'ot_payment_rate': ot_payment_rate, 'net_salary': net_salary, 'total_advance_amount': total_advance_amount, 'epf': epf, 'total_allowance': total_allowance, 'room_charge':room_charge}, status=200)
        
