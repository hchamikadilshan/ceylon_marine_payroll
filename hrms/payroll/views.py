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

# Create your views here.


class EmployeeSalaryPdfView(View):
    def post(self,request):
        emp_id = request.POST['attendance_view_emp_id']
        year_month = request.POST["attendance_view_month_year"]

        year_month_split = year_month.split('-')
        emp = Employee.objects.get(emp_id=emp_id)
        attendance_record = Attendance.objects.filter(
            employee=emp, date__month=year_month_split[1]).order_by('date').values()
        attendance_record_list = list(attendance_record)
        total_working_hours = 0
        total_ot_hours = 0
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
            daily_payment_rate = employee_finance.daily_payment
            hourly_payment_rate = daily_payment_rate/8
            ot_payment_rate = employee_finance.ot_payment_rate
            basic_salary = total_working_hours * hourly_payment_rate
            ot_payment = total_ot_hours * ot_payment_rate

            net_salary = basic_salary + ot_payment

            ot_payment = "{:.2f}".format(ot_payment)
            ot_payment_rate = "{:.2f}".format(ot_payment_rate)
            hourly_payment_rate = "{:.2f}".format(hourly_payment_rate)
            basic_salary = "{:.2f}".format(basic_salary)
            net_salary = "{:.2f}".format(net_salary)
        except EmployeeFinance.DoesNotExist:
            print("Employee Finance Does not exists")


# -------------------------------------------------------------------------------------
        salary_data = []
        salary_details_row_1 = [
            "Basic Salary", f"{hourly_payment_rate} x {total_working_hours}", basic_salary]
        salary_data.append(salary_details_row_1)

        buffer = io.BytesIO()
        file_name = f"{emp_id}_{year_month}_Salary_Details.pdf"
        title = f"{emp_id}_{year_month}_Salary_Details"
        pdf = SimpleDocTemplate(buffer,pagesize = A4, title=title)
        elements = []
        attendance_table = Table(table_data)
        salary_table = Table(salary_data)
        attendance_table_styles = TableStyle(
            [
             ('SPAN', (0, 0), (-1, 0)),
             ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
             ('SPAN', (0, 1), (-1, 1)),
             ('SPAN', (3, 2), (-1, 2)),
             ('SPAN', (3, 3), (-1, 3)),
             ('GRID', (0, 2), (-1, 2), 1, colors.black),
             ('GRID', (0, 3), (-1, 3), 1, colors.black),
             ('BOX', (0, 4), (-1, -1), 1, colors.black),
             ('GRID', (0, 4), (-1, -1), 1, colors.black),
             ('ALIGN', (2, 4), (5, -1),'RIGHT'),
             

             ]
            
        )
        salary_table_styles = TableStyle(
            [
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]
        )
        attendance_table.setStyle(attendance_table_styles)
        salary_table.setStyle(salary_table_styles)
        elements.append(attendance_table)
        elements.append(salary_table)
        pdf.build(elements)
        buffer.seek(0)
        
        return FileResponse(buffer, as_attachment=True, filename=file_name)

class AllowancesView(View):
    def get(self,request):
        return render(request,'allowances.html')


class AdvancePaymentsView(View):
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



class PayRollTestView(View):
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
        total_working_hours = 0
        total_ot_hours = 0

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

        try:
            employee_finance = EmployeeFinance.objects.filter(
                employee=emp).order_by('-submit_date').first()
            daily_payment_rate = employee_finance.daily_payment
            hourly_payment_rate = daily_payment_rate/8
            ot_payment_rate = employee_finance.ot_payment_rate
            basic_salary = total_working_hours * hourly_payment_rate
            ot_payment = total_ot_hours * ot_payment_rate

            net_salary = basic_salary + ot_payment

            ot_payment = "{:.2f}".format(ot_payment)
            ot_payment_rate = "{:.2f}".format(ot_payment_rate)
            hourly_payment_rate = "{:.2f}".format(hourly_payment_rate)
            basic_salary = "{:.2f}".format(basic_salary)
            net_salary = "{:.2f}".format(net_salary)
        except EmployeeFinance.DoesNotExist:
            print("Employee Finance Does not exists")

        return JsonResponse({'attendance_list': attendance_record_list, 'total_working_hours': total_working_hours, 'total_ot_hours': total_ot_hours, 'basic_salary': basic_salary, 'ot_payment': ot_payment, 'hourly_payment_rate': hourly_payment_rate, 'ot_payment_rate': ot_payment_rate, 'net_salary': net_salary}, status=200)
        
