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
from reportlab.pdfgen import canvas
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
        attendance_allowance = 0
# ----------------------------------------------------------------------------------------
        # Adding Heading Data
        table_data = []
        document_heading_1 = ['Attendance Report']
        document_heading_2 = [""]
        document_heading_3 = ["Emp ID :",emp_id,"Emp Name :",emp.name]
        document_heading_4 = ["Month :",year_month,"Department :",emp.department]
        table_heading = ['Date', 'Day', 'In Time',
                         'Out Time', 'Working Hours', 'OT Hours','Remarks']
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
                if (record['day'] == "Saturday" and ((out_time_obj - in_time_obj).total_seconds()/(60*60) >=8)):
                    ot_hours = ot_hours + 3
                elif (record['day'] == "Sunday" and ((out_time_obj - in_time_obj).total_seconds()/(60*60) >=8)):
                    ot_hours = ot_hours + 4
                elif (record['special_holiday'] == 1 and ((out_time_obj - in_time_obj).total_seconds()/(60*60) >=8)):
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
# Advance Payment Calculation
        try:
            employee_finance = EmployeeFinance.objects.filter(
                employee=emp).order_by('-submit_date').first()
            if employee_finance is not None:
                daily_payment_rate = employee_finance.daily_payment
                ot_payment_rate = employee_finance.ot_payment_rate
                room_charge = employee_finance.room_charge
                fixed_basic_salary = employee_finance.basic_salary
                br_payment = employee_finance.br_payment
            else:
                return JsonResponse({'error':"no employee finance data"})
            # daily_payment_rate = employee_finance.daily_payment
            hourly_payment_rate = daily_payment_rate/8
            # ot_payment_rate = employee_finance.ot_payment_rate
            basic_salary = total_working_hours * hourly_payment_rate
            ot_payment = total_ot_hours * ot_payment_rate

# Room Charges
            
            net_salary = basic_salary + ot_payment - room_charge
            fixed_allowance = basic_salary - fixed_basic_salary - br_payment
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

            
        except EmployeeFinance.DoesNotExist:
            print("Employee Finance Does not exists")
# Calculating Attendance Allowance
        if len(attendance_record_list) >= 26:
            attendance_allowance = attendance_allowance + 1000
        if len(attendance_record_list) > 26:
            attendance_allowance = attendance_allowance + (len(attendance_record_list)-26)*500
# Formating Values
        total_payments = fixed_basic_salary + br_payment + fixed_allowance + total_allowance + ot_payment 
        total_deductions = total_advance_amount + room_charge + epf

        total_deductions = "{:>9.2f}".format(total_deductions)
        total_payments = "{:>9.2f}".format(total_payments)
        attendance_allowance = "{:>9.2f}".format(attendance_allowance)
        fixed_allowance = "{:>9.2f}".format(fixed_allowance)
        br_payment = "{:>9.2f}".format(br_payment)
        fixed_basic_salary = "{:>9.2f}".format(fixed_basic_salary)
        room_charge = "{:>9.2f}".format(room_charge)
        epf = "{:>9.2f}".format(epf)
        total_advance_amount = "{:>9.2f}".format(total_advance_amount)
        total_allowance = "{:>9.2f}".format(total_allowance)
        ot_payment = "{:>9.2f}".format(ot_payment)
        ot_payment_rate = "{:>9.2f}".format(ot_payment_rate)
        hourly_payment_rate = "{:>9.2f}".format(hourly_payment_rate)
        basic_salary = "{:>9.2f}".format(basic_salary)
        net_salary = "{:>9.2f}".format(net_salary) 


# -------------------------------------------------------------------------------------
        empty_row = ["","","","","","",""]
        
        salary_details_row_1 = [
            "Basic Salary", fixed_basic_salary,"","","",  "", ""]
        salary_details_row_2 = [
            "B-R Payment", br_payment,"","", "", "", ""]
        salary_details_row_3 = [
            "Fixed Allowance", fixed_allowance,"","", "", "", ""]
        salary_details_row_4 = [
            "Total OT Payment",ot_payment,"","", "", "", ""]
        salary_details_row_5 = [
            "Attendance Allowance",f"{attendance_allowance}","","", "", "", ""]
        salary_details_row_6 = [
            "Allowance", total_allowance,"","", "", total_payments]
        salary_details_row_7 = [
            "Salary Advance", f"({total_advance_amount})", "","","" ,"", ""]
        salary_details_row_8 = [
            "EPF", f"({epf})","","","","",""]
        salary_details_row_9 = [
            "Room Charge",f"({room_charge})","","", "",f"({total_deductions})" ]
        salary_details_row_10 = [
            "Net Payment", "", "", "", "", net_salary]
            
        # table_data.append(empty_row)
        
        table_data.append(salary_details_row_1)
        table_data.append(salary_details_row_2)
        table_data.append(salary_details_row_3)
        table_data.append(salary_details_row_4)
        table_data.append(salary_details_row_5)
        table_data.append(salary_details_row_6)
        table_data.append(salary_details_row_7)
        table_data.append(salary_details_row_8)
        table_data.append(salary_details_row_9)
        table_data.append(salary_details_row_10)

        buffer = io.BytesIO()
        file_name = f"{emp_id}_{year_month}_Salary_Details.pdf"
        title = f"{emp_id}_{year_month}_Salary_Details"
        
        pdf = SimpleDocTemplate(buffer,pagesize = A4, title=title,showBoundary=1,leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0,)
        elements = []
        attendance_table = Table(table_data)
        # salary_table = Table(salary_data)
        attendance_table_styles = TableStyle(
            [
            #  ('SPAN', (0, 0), (-1, 0)),
            #  ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            #  ('SPAN', (0, 0), (-1, 0)),
             ('SPAN', (3, 0), (-1, 0)),
             ('SPAN', (3, 1), (-1, 1)),
             ('SPAN', (1, -10), (4, -10)),  # Basic Salary Row
             ('SPAN', (5, -10), (6, -10)),
             ('SPAN', (1, -9), (4, -9)),  # Basic Salary Row
             ('SPAN', (5, -9), (6, -9)),
             ('SPAN', (1, -8), (4, -8)),  # B-R Row
             ('SPAN', (5, -8), (6, -8)),
             ('SPAN', (1, -7), (4, -7)),  # Fixed Allowance Row
             ('SPAN', (5, -7), (6, -7)),
             ('SPAN', (1, -6), (4, -6)),  # OT Row
             ('SPAN', (5, -6), (6, -6)),
             ('SPAN', (1, -5), (4, -5)),  # EPF Row
             ('SPAN', (5, -5), (6, -5)),
             ('SPAN', (1, -4), (4, -4)),  # Room Charge Row
             ('SPAN', (5, -4), (6, -4)),
             ('SPAN', (1, -3), (4, -3)),  # Net Payment Row
             ('SPAN', (5, -3), (6, -3)),
             ('SPAN', (1, -2), (4, -2)),  # Net Payment Row
             ('SPAN', (5, -2), (6, -2)),
             ('SPAN', (1, -1), (4, -1)),  # Net Payment Row
             ('SPAN', (5, -1), (6, -1)),
             ('GRID', (0, 0), (-1, -1), 1, colors.black),
             ('GRID', (0, 1), (-1, 1), 1, colors.black),
             ('BOX', (0, 4), (-1, -1), 1, colors.black),
             ('GRID', (0, 4), (-1, -1), 1, colors.black),
             ('ALIGN', (2, 4), (5, -1),'RIGHT'),
             ('ALIGN', (1, -10), (-1, -1),'RIGHT'),
             ('FONT', (0, 0), (-1, -1), 'Helvetica',12),
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

        pdf1= canvas.Canvas(buffer,pagesize = A4)
        
        return FileResponse(buffer, as_attachment=True, filename=file_name)
def get_final_salary_details(emp_id="",month="",emp_type=""):
# Getting Details of one employee one month
    if emp_id != "" and month != "":

        emp = Employee.objects.get(emp_id=emp_id)
        attendance_record = Attendance.objects.filter(
                employee=emp,date__month=month).order_by('date').values()
        attendance_record_list = list(attendance_record)
        min_salary_amount = 16600.0
        total_working_hours = 0
        total_ot_hours = 0
        epf = 0
        attendance_allowance = 0


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
                if (record['day'] == "Saturday" and ((out_time_obj - in_time_obj).total_seconds()/(60*60) >=8)):
                    ot_hours = ot_hours + 3
                elif (record['day'] == "Sunday" and ((out_time_obj - in_time_obj).total_seconds()/(60*60) >=8)):
                    ot_hours = ot_hours + 4
                elif (record['special_holiday'] == 1 and ((out_time_obj - in_time_obj).total_seconds()/(60*60) >=8)):
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
                fixed_basic_salary = employee_finance.basic_salary
                br_payment = employee_finance.br_payment
            else:
                return "employee_finance_details_error"
                # return JsonResponse({'error':"no employee finance data"})
            # daily_payment_rate = employee_finance.daily_payment
            hourly_payment_rate = daily_payment_rate/8
            # ot_payment_rate = employee_finance.ot_payment_rate
            basic_salary = total_working_hours * hourly_payment_rate
            ot_payment = total_ot_hours * ot_payment_rate

# Room Charges
            
            net_salary = basic_salary + ot_payment - room_charge
            fixed_allowance = basic_salary - fixed_basic_salary - br_payment
            try:
                advance_payment_data = SalaryAdvance.objects.filter(
                    employee=emp, date__month=month).order_by('date').values()
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
                    employee=emp, date__month=month,status =True).order_by('date').values()
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

            
        except EmployeeFinance.DoesNotExist:
            print("Employee Finance Does not exists")
# Calculating Attendance Allowance
        if len(attendance_record_list) >= 26:
            attendance_allowance = attendance_allowance + 1000
        if len(attendance_record_list) > 26:
            attendance_allowance = attendance_allowance + (len(attendance_record_list)-26)*500

        return [attendance_allowance,fixed_allowance,br_payment,fixed_basic_salary,room_charge,epf,total_advance_amount,total_allowance,ot_payment,ot_payment_rate,hourly_payment_rate,basic_salary,net_salary,attendance_record_list,total_working_hours,total_ot_hours]
    elif (emp_id =="" and emp_type =="" and month !=""):
        attendance_record = Attendance.objects.filter(date__month=month).order_by('date')
        employees = Employee.objects.filter(emp_type=0,active_status=True).values()
        employees_list = list(employees)
        for employee in employees_list:
            emp_id = employee["emp_id"]
        return
class PayslipInfo(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def post(self,request):
        # Employee ID and Month
        if request.POST["type"] == "id_month":
            emp_id = request.POST["emp_id"]
            year_month = request.POST["month"]
            year_month_split = year_month.split('-')
            try :
                response = get_final_salary_details(emp_id=emp_id,month=year_month_split[1])
                return JsonResponse({})
            except ValueError:
                return JsonResponse({"error":"attendance_record_error"})
        elif request.POST["type"] == "month":
            year_month = request.POST["month"]
            year_month_split = year_month.split('-')
            employees = Employee.objects.filter(emp_type=0,active_status=True).values()
            employees_list = list(employees)
            payslips_record = []
            for employee in employees_list:
                emp_id = employee["emp_id"]
                print(emp_id)
                try :
                    response = get_final_salary_details(emp_id=emp_id,month=year_month_split[1])
                    payslips_record.append({'emp_id':emp_id,"name":employee["name"],"status":0})
                except (ValueError,IndexError):
                    payslips_record.append({'emp_id':emp_id,"name":employee["name"],"status":1})
            print(payslips_record)
            return JsonResponse({"data":payslips_record})
        elif request.POST["type"] == "id":
            # year_month = request.POST["month"]
            # year_month_split = year_month.split('-')
            # employees = Employee.objects.filter(emp_type=0,active_status=True).values()
            # employees_list = list(employees)
            # payslips_record = []
            # for employee in employees_list:
            #     emp_id = employee["emp_id"]
            #     print(emp_id)
            #     try :
            #         response = get_final_salary_details(emp_id=emp_id,month=year_month_split[1])
            #         payslips_record.append({'emp_id':emp_id,"name":employee["name"],"status":0})
            #     except (ValueError,IndexError):
            #         payslips_record.append({'emp_id':emp_id,"name":employee["name"],"status":1})
            # print(payslips_record)
            return JsonResponse({})
            
class PayslipPdfView(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def get(self,request):
        user = request.user
        get_final_salary_details(emp_id="A07176",month="02")
        return render (request,'payslips.html',context={'users':user})
    def post(self,request):
        return JsonResponse({})

class AllowancesView(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def get(self,request):
        user = request.user
        return render(request,'allowances.html',context={'user':user})

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
class EditAdvancePayment(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def post(self,request):
        emp_id = request.POST['emp_id']
        date = request.POST['date']
        amount = request.POST['amount']
        status = request.POST['status']
        id = request.POST["id"]
        emp = Employee.objects.get(emp_id=emp_id)
        time_stamp = datetime.now()

        advance_record = SalaryAdvance.objects.get(
            employee=emp, id=id)
        advance_record.date = date
        advance_record.amount=amount
        advance_record.status= (True if status == "true" else False)
        advance_record.time_stamp = time_stamp
        advance_record.save()
        return JsonResponse({})
class AdvancePaymentsView(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def get(self, request):
        user = request.user
        return render(request, 'advance_payment.html',context={'user':user})
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
        user = request.user
        return render(request, 'payroll_test.html',context={'user':user})

    def post(self, request):
        emp_id = request.POST['emp_id']
        year_month = request.POST["month"]
        year_month_split = year_month.split('-')

        
# Formating Values
        response = get_final_salary_details(emp_id=emp_id,month=year_month_split[1])
        if response == "employee_finance_details_error":
            return JsonResponse({'error':"no employee finance data"})
        else:

            attendance_allowance = "{:>9.2f}".format(response[0])
            fixed_allowance = "{:>9.2f}".format(response[1])
            br_payment = "{:>9.2f}".format(response[2])
            fixed_basic_salary = "{:>9.2f}".format(response[3])
            room_charge = "{:>9.2f}".format(response[4])
            epf = "{:>9.2f}".format(response[5])
            total_advance_amount = "{:>9.2f}".format(response[6])
            total_allowance = "{:>9.2f}".format(response[7])
            ot_payment = "{:>9.2f}".format(response[8])
            ot_payment_rate = "{:>9.2f}".format(response[9])
            hourly_payment_rate = "{:>9.2f}".format(response[10])
            basic_salary = "{:>9.2f}".format(response[11])
            net_salary = "{:>9.2f}".format(response[12])

            return JsonResponse({'attendance_list': response[13], 'total_working_hours': response[14], 'total_ot_hours': response[15], 'basic_salary': basic_salary, 'ot_payment': ot_payment, 'hourly_payment_rate': hourly_payment_rate, 'ot_payment_rate': ot_payment_rate, 'net_salary': net_salary, 'total_advance_amount': total_advance_amount, 'epf': epf, 'total_allowance': total_allowance, 'room_charge':room_charge,"fixed_basic_salary":fixed_basic_salary,'br_payment':br_payment,'fixed_allowance':fixed_allowance,'attendance_allowance':attendance_allowance}, status=200)
        
