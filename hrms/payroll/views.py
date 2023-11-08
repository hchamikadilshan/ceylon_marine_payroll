from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse,FileResponse
from employee.models import Employee, EmployeeFinance
from attendance.models import Attendance
from django.db.models import Avg, Case, Count, F,Subquery
from datetime import  datetime,timedelta
from .models import SalaryAdvance,Alllowance,Deduction
from django.db.models.functions import Coalesce
import locale
import io
from reportlab.lib.pagesizes import A4,landscape
from reportlab.platypus import SimpleDocTemplate,Table,TableStyle,Frame
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch,cm
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
                    if (in_time_obj < attendance_in_time) and emp.dprtmnt.department in ["TRANSPORT","BUFFE","TEA CENTRE","WELFARE","KITCHEN","3RD FLLOR"] :
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
                if (record['day'] == "Saturday" and ((out_time_obj - in_time_obj).total_seconds()/(60*60) >=8) and (record['special_holiday'] != 1 )):
                    ot_hours = ot_hours + 3
                elif (record['day'] == "Sunday" and ((out_time_obj - in_time_obj).total_seconds()/(60*60) >=8) and (record['special_holiday'] != 1 )):
                    ot_hours = ot_hours + 4
                elif (record['special_holiday'] == 1 and ((out_time_obj - in_time_obj).total_seconds()/(60*60) >=8)):
                    ot_hours = ot_hours + 4
# Next Day Out
            else: 
                
# Out time O/T Hours Calculation
                if (record['day'] == "Saturday" ) and (record['special_holiday'] != 1 ):
                    ot_hours = ot_hours + 3
                elif (record['day'] == "Sunday" ) and (record['special_holiday'] != 1 ):
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
def get_no_of_days_of_the_month(month):
    days = 0
    if month in ["01","03","05","07","08","10","12"]:
        days = 31
    elif month in ["04","06","09","11"]:
        days = 30
    elif month == "02":
        days = 28
    return days
    
def get_process_salary(request_type,month,emp_id="",emp_type=0):
    employees_list = []
    # Getting data of one employee
    if request_type == "single":
        # Getting employee object
        employee = Employee.objects.get(emp_id=emp_id)
        attendance_record = Attendance.objects.filter(
                employee=employee,date__month=month).order_by('date').values()
        attendance_record_list = list(attendance_record)
        # Getting employee finance
        try:
            employee_finances = EmployeeFinance.objects.filter().values()
            employee_finance = employee_finances.filter(employee = employee).order_by('-submit_date').first()

        except EmployeeFinance.DoesNotExist:
            return "employee_finance_details_error"
        # Getting employee salary advance
        try:
            advance_payment_data = SalaryAdvance.objects.filter(
                employee=employee, date__month=month).order_by('date').values()
            advance_payment_data_list = list(advance_payment_data)
        except SalaryAdvance.DoesNotExist:
            advance_payment_data_list =[]
            print("Salary Advances does not exists")
        # Getting employee allowance
        try:
            allowance_data = Alllowance.objects.filter(
                employee=employee, date__month=month,status =True).order_by('date').values()
            allowance_data_list = list(allowance_data)
        except Alllowance.DoesNotExist:
            allowance_data_list =[]
            print("No Allowance")
        
        employees_list.append([employee,attendance_record_list,employee_finance,advance_payment_data_list,allowance_data_list])

    # Getting Data of multiple employees
    elif request_type == "multiple":
        # Getting employee objects
        employees = Employee.objects.filter(emp_type=emp_type,active_status = 1)

        # Getting attendance records
        attendance_records = Attendance.objects.filter(date__month=month).order_by('employee','date').values()
        # Getting finance records
        employee_finances = EmployeeFinance.objects.filter().values()  

        advance_payment_data = SalaryAdvance.objects.filter(date__month=month).order_by('date').values()


        allowance_data = Alllowance.objects.filter(date__month=month,status =True).order_by('date').values()


        for employee in employees:
            employee_attendance_record = attendance_records.filter(employee=employee) 
            employee_attendance_record_list = list(employee_attendance_record)
            employee_finance_record = employee_finances.filter(employee = employee).order_by('-submit_date').first()
            employee_advance_payment_records = advance_payment_data.filter(employee=employee)
            employee_advance_payment_records_list = list(employee_advance_payment_records)
            employee_allowance_data = allowance_data.filter(employee=employee)
            employee_allowance_data_list = list(employee_allowance_data)
            # print(employee,employee_attendance_record_list,employee_finance_record,employee_advance_payment_records_list,employee_allowance_data_list)
            employees_list.append([employee,employee_attendance_record_list,employee_finance_record,employee_advance_payment_records_list,employee_allowance_data_list])       
        
    return employees_list

def calculate_salary(employee,attendance_record,finance_record,advance_payemnt,allowance_data,month):
    emp = employee
    attendance_record_list = attendance_record
    min_salary_amount = 16600.0
    total_working_hours = 0
    total_ot_hours = 0
    epf = 0
    attendance_allowance = 0
    over_night_days = 0

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
            if emp.emp_id == "A04456" or emp.emp_id == "A04455":
                    print(f"intime outtime {in_time_obj}-{out_time_obj}:")
            if (in_time_obj == attendance_in_time or out_time_obj == attendance_out_time):
                pass
# Deducting the punishment hours
            elif (in_time_obj > attendance_in_time or out_time_obj < attendance_out_time):
                if emp.emp_id == "A04456" or emp.emp_id == "A04455":
                    print(f"intime {in_time_obj}:")
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
                    if emp.emp_id == "A04456" or emp.emp_id == "A04455":
                        print(f"dedction_working_hour:{in_time_obj} - {normal_working_hours}")
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
                    if emp.emp_id == "A04456" or emp.emp_id == "A04455":
                        print(f"dedction_working_hour:{out_time_obj} - {normal_working_hours}")
            if ((out_time_obj <= attendance_out_time_noon)):
                pass
            else:
                normal_working_hours = normal_working_hours - 1
            
# O/T Hours Calculation
            if (in_time_obj <= attendance_in_time or out_time_obj >= attendance_out_time):
                if emp.dprtmnt is None:
                    return "Department Empty"
                else:
                    if (in_time_obj <= attendance_in_time) and emp.dprtmnt.department in ["TRANSPORT","BUFFE","TEA CENTRE","WELFARE","KITCHEN","3RD FLLOR"] :
                        in_time_difference_ot = attendance_in_time - in_time_obj
                        in_time_difference_ot_hours = in_time_difference_ot.total_seconds()/(60*60)
                        a = (in_time_difference_ot.total_seconds()/(60*60))//0.5
                        b = (in_time_difference_ot.total_seconds()/(60*60)) % 0.5
                        if in_time_difference_ot_hours < 0.5:
                            pass
                        elif in_time_difference_ot_hours >= 0.5:
                            ot_hours = ot_hours + (0.5 * a) 
                    if out_time_obj >= attendance_out_time:
                        out_time_difference_ot = out_time_obj - attendance_out_time
                        out_time_difference_ot_hours = out_time_difference_ot.total_seconds()/(60*60)
                        a = (out_time_difference_ot_hours//0.5)
                        b = (out_time_difference_ot_hours % 0.5)
                        if out_time_difference_ot_hours < 0.5:
                            pass
                        elif out_time_difference_ot_hours >= 0.5:
                            ot_hours = ot_hours + (0.5 * a) 
            if (record['day'] == "Saturday" and ((out_time_obj - in_time_obj).total_seconds()/(60*60) >=8) and (record['special_holiday'] != 1 ) and (in_time_obj <= attendance_in_time and out_time_obj >= attendance_out_time)):
                    ot_hours = ot_hours + 3
            elif (record['day'] == "Sunday" and ((out_time_obj - in_time_obj).total_seconds()/(60*60) >=8) and (record['special_holiday'] != 1 ) and (in_time_obj <= attendance_in_time and out_time_obj >= attendance_out_time)):
                    ot_hours = ot_hours + 4
            elif (record['special_holiday'] == 1 and ((out_time_obj - in_time_obj).total_seconds()/(60*60) >=8) and (in_time_obj <= attendance_in_time and out_time_obj >= attendance_out_time)):
                    ot_hours = ot_hours + 4
# Next Day Out
        else: 
            
# Out time O/T Hours Calculation
            if (in_time_obj <= attendance_in_time) and (out_time_obj >= attendance_in_time):
                over_night_days += 1
            if (record['day'] == "Saturday" ) and (record['special_holiday'] != 1 ):
                ot_hours = ot_hours + 3
            elif (record['day'] == "Sunday" ) and (record['special_holiday'] != 1 ):
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
        if emp.emp_id == "A04456" or emp.emp_id == "A04455":
            print(record["working_hours"])
        total_working_hours = total_working_hours + record['working_hours']
        total_ot_hours = total_ot_hours + record['ot_hours']
# Advance Payment Calculation
    
    employee_finance = finance_record
    if (employee_finance is not None) and (employee_finance["daily_payment"] != 0.0 and employee_finance["ot_payment_rate"] != 0.0 and employee_finance["basic_salary"] != 0.0):
        daily_payment_rate = employee_finance["daily_payment"]
        ot_payment_rate = employee_finance["ot_payment_rate"]
        room_charge = employee_finance["room_charge"]
        fixed_basic_salary = employee_finance["basic_salary"]
        br_payment = employee_finance["br_payment"]
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
    
    # advance_payment_data = SalaryAdvance.objects.filter(
    #     employee=emp, date__month=month).order_by('date').values()
    advance_payment_data_list = advance_payemnt
    total_advance_amount = 0
    for advance in advance_payment_data_list:
        total_advance_amount = total_advance_amount + advance["amount"]
    net_salary = net_salary - total_advance_amount


# Allowances Calculation 
  
    # allowance_data = Alllowance.objects.filter(
    #     employee=emp, date__month=month,status =True).order_by('date').values()
    allowance_data_list = allowance_data
    total_allowance = 0
    allowances = []
    for allowance in allowance_data_list:
        allowances.append([allowance["description"],allowance["amount"]])
        total_allowance = total_allowance + allowance["amount"]

# Calculating Attendance Allowance
    attendance_allowance_26 = 0
    extra_days = 0
    extra_attendance_allowance = 0
    worked_days = len(attendance_record_list) + over_night_days
    if worked_days >= 26:
        attendance_allowance_26 = 1000
        attendance_allowance = attendance_allowance + 1000
    if worked_days > 26:
        extra_days = worked_days-26
        extra_attendance_allowance = (worked_days-26)*500
        attendance_allowance = attendance_allowance + (worked_days-26)*500

    calculated_fixed_basic_salary =  br_payment + fixed_basic_salary 

# EPF Calculation
        
    if employee_finance["epf_type"] == "1":
        if calculated_fixed_basic_salary > basic_salary:
            epf = epf + (basic_salary * 0.08)
        else:
            epf = epf + (min_salary_amount * 0.08)
    elif employee_finance["epf_type"] == "2":
        pass
    net_salary = net_salary - epf + total_allowance + attendance_allowance

# Calculate salary if attendance payment is less than fixed payment   
    calculated_fixed_basic_salary =  br_payment + fixed_basic_salary

    if calculated_fixed_basic_salary > basic_salary:
        br_payment = 140 * worked_days
        fixed_basic_salary = basic_salary - br_payment
        if fixed_basic_salary > 13100.0:
            fixed_allowance =  fixed_basic_salary - 13100.0
            fixed_basic_salary = 13100.0
        else:
            fixed_allowance = 0.0
        net_salary = basic_salary + ot_payment - room_charge - total_advance_amount - epf + total_allowance + attendance_allowance
    if emp.emp_id == "A04456" or emp.emp_id == "A04455":
        print(f"employee:{emp.emp_id}")
        print(f"total_salary:{net_salary}")    
        print(f"attendance_payment : {basic_salary}")
        print(f"worked_hours:{total_working_hours}")
        print(f"ot_payment :{ot_payment}")
        print(f"room_charge:{room_charge}")
        print(f"total_advance_amount:{total_advance_amount}")
        print(f"epf:{epf}")
        print(f"total_allowance{total_allowance}")
        print(f"attendance_allowance:{attendance_allowance}")
        print("--------------")
    return [attendance_allowance,fixed_allowance,br_payment,fixed_basic_salary,room_charge,epf,total_advance_amount,total_allowance,ot_payment,ot_payment_rate,hourly_payment_rate,basic_salary,net_salary,attendance_record_list,total_working_hours,total_ot_hours,attendance_allowance_26,extra_days,extra_attendance_allowance,employee.nic_no,employee.emp_id,employee.name,employee.dprtmnt.department,employee.epf_no,allowances,worked_days]


def get_final_salary_details(emp,month="",year=""):
    emp = emp
# Calculating Salary of Normal Employee
    if emp.emp_type == 0:
        # print(emp.emp_id)
        attendance_record = Attendance.objects.filter(
                            employee=emp,date__month=month,date__year=year).order_by('date').values()
        attendance_record_list = list(attendance_record)
        min_salary_amount = 16600.0
        total_working_hours = 0
        total_ot_hours = 0
        epf = 0
        epf_12 =0
        attendance_allowance = 0
        over_night_days = 0
        try :
            employee_finance = EmployeeFinance.objects.filter(
                employee=emp,effective_from__month__lte = month).order_by("-effective_from",'-submit_date').first()
            if employee_finance ==  None:
                return "employee_finance_details_error"
        except EmployeeFinance.DoesNotExist:
            print("Employee Finance Does not exists")

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
        

            if record['next_day'] == 0 and record['night_shift'] == False:
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
                    if emp.dprtmnt is None:
                        return "Department Empty"
                    else:
                        if (in_time_obj <= attendance_in_time) and (emp.dprtmnt.department in ["TRANSPORT","BUFFE","TEA CENTRE","WELFARE","KITCHEN","3RD FLOOR"] or employee_finance.morning_ot == "1") :
                            
                            in_time_difference_ot = attendance_in_time - in_time_obj
                            in_time_difference_ot_hours = in_time_difference_ot.total_seconds()/(60*60)
                            a = (in_time_difference_ot.total_seconds()/(60*60))//0.5
                            b = (in_time_difference_ot.total_seconds()/(60*60)) % 0.5
                            if in_time_difference_ot_hours < 0.5:
                                pass
                            elif in_time_difference_ot_hours >= 0.5:
                                ot_hours = ot_hours + (0.5 * a) 
                        if out_time_obj >= attendance_out_time:
                            out_time_difference_ot = out_time_obj - attendance_out_time
                            out_time_difference_ot_hours = out_time_difference_ot.total_seconds()/(60*60)
                            a = (out_time_difference_ot_hours//0.5)
                            b = (out_time_difference_ot_hours % 0.5)
                            if out_time_difference_ot_hours < 0.5:
                                pass
                            elif out_time_difference_ot_hours >= 0.5:
                                ot_hours = ot_hours + (0.5 * a) 
                if (record['day'] == "Saturday" and ((out_time_obj - in_time_obj).total_seconds()/(60*60) >=8) and (record['special_holiday'] != 1 ) and (in_time_obj <= attendance_in_time and out_time_obj >= attendance_out_time)):
                    ot_hours = ot_hours + 3
                elif (record['day'] == "Sunday" and ((out_time_obj - in_time_obj).total_seconds()/(60*60) >=8) and (record['special_holiday'] != 1 ) and (in_time_obj <= attendance_in_time and out_time_obj >= attendance_out_time)):
                    ot_hours = ot_hours + 4
                elif (record['special_holiday'] == 1 and ((out_time_obj - in_time_obj).total_seconds()/(60*60) >=8) and (in_time_obj <= attendance_in_time and out_time_obj >= attendance_out_time)):
                    ot_hours = ot_hours + 4
# Night Shift
            elif record['night_shift'] == True:
                if (in_time_obj > out_time_obj):
                    normal_working_hours = normal_working_hours - 1
                    worked_hours_before_12 = 24-((in_time_obj -attendance_out_time_mid_night).total_seconds()/(60*60))
                    worked_hours_after_12 = -(attendance_out_time_mid_night - out_time_obj).total_seconds()/(60*60)
                    total_worked_hours = worked_hours_before_12 + worked_hours_after_12
                    if total_worked_hours <= 8:
                        normal_working_hours = total_worked_hours
                    else:
                        normal_working_hours = 8
                        ot_hours = total_worked_hours - 8
                    if (record['day'] == "Saturday" and (total_worked_hours >= 8) and (record['special_holiday'] != 1 )):
                        ot_hours = ot_hours + 3
                    elif (record['day'] == "Sunday" and (total_worked_hours >= 8) and (record['special_holiday'] != 1 )):
                        ot_hours = ot_hours + 4
                    elif (record['special_holiday'] == 1 and (total_worked_hours >= 8) ):
                        ot_hours = ot_hours + 4
                elif(in_time_obj < out_time_obj):
                    normal_working_hours = normal_working_hours - 1
                    worked_hours = (out_time_obj - in_time_obj).total_seconds()/(60*60)
                    if worked_hours <= 8:
                        normal_working_hours = worked_hours
                    else:
                        normal_working_hours = 8
                        ot_hours = worked_hours - 8 
                    if (record['day'] == "Saturday" and (worked_hours >= 8) and (record['special_holiday'] != 1 )):
                        ot_hours = ot_hours + 3
                    elif (record['day'] == "Sunday" and (worked_hours >= 8) and (record['special_holiday'] != 1 )):
                        ot_hours = ot_hours + 4
                    elif (record['special_holiday'] == 1 and (worked_hours >= 8) ):
                        ot_hours = ot_hours + 4
                    

# Next Day Out
            elif record["next_day"]== True and record["night_shift"] ==  False: 
                
# Out time O/T Hours Calculation
                if (in_time_obj <= attendance_in_time) and (out_time_obj >= attendance_in_time):
                    over_night_days += 1
                if (record['day'] == "Saturday" ) and (record['special_holiday'] != 1 ):
                    ot_hours = ot_hours + 3
                elif (record['day'] == "Sunday" ) and (record['special_holiday'] != 1 ):
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
                employee=emp,effective_from__month__lte = month,effective_from__year__lte = year).order_by("-effective_from",'-submit_date').first()
            if (employee_finance is not None) and (employee_finance.daily_payment != 0.0 and employee_finance.ot_payment_rate != 0.0 and employee_finance.basic_salary != 0.0):
                daily_payment_rate = employee_finance.daily_payment
                ot_payment_rate = employee_finance.ot_payment_rate
                room_charge = employee_finance.room_charge
                fixed_basic_salary = employee_finance.basic_salary
                br_payment = employee_finance.br_payment
                epf_status = employee_finance.epf_type
            else:
                epf_status = None
                return "employee_finance_details_error"

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
                    employee=emp, date__month=month,date__year=year).order_by('date').values()
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
                    employee=emp, date__month=month,status =True,date__year=year).order_by('date').values()
                allowance_data_list = list(allowance_data)
                total_allowance = 0
                allowances = []
                for allowance in allowance_data_list:
                    allowances.append([allowance["description"],allowance["amount"]])
                    total_allowance = total_allowance + allowance["amount"]
            except Alllowance.DoesNotExist:
                print("No Allowance")
#  Deduction Calculation 
            try:
                deduction_data = Deduction.objects.filter(
                    employee=emp, date__month=month,status =True,date__year=year).order_by('date').values()
                deduction_data_list = list(deduction_data)
                total_deduction = 0
                deductions = []
                for deduction in deduction_data_list:
                    deductions.append([deduction["description"],deduction["amount"]])
                    total_deduction = total_deduction + deduction["amount"]
            except Deduction.DoesNotExist:
                print("No Allowance")
# Calculating Attendance Allowance
            attendance_allowance_26 = 0
            extra_days = 0
            extra_attendance_allowance = 0
            worked_days = len(attendance_record_list) + over_night_days
            
            if worked_days >= 26:
                attendance_allowance_26 = 1000
                attendance_allowance = attendance_allowance + 1000
            if worked_days > 26:
                
                extra_days = worked_days-26
                extra_attendance_allowance = (worked_days-26)*500
                attendance_allowance = attendance_allowance + (worked_days-26)*500

            calculated_fixed_basic_salary =  br_payment + fixed_basic_salary 

# EPF Calculation
            if employee_finance.epf_type == "1":
                if calculated_fixed_basic_salary > basic_salary:
                    epf = epf + (basic_salary * 0.08)
                    epf_12 = epf_12 + (basic_salary * 0.12)
                else:
                    epf = epf + (min_salary_amount * 0.08)
                    epf_12 = epf_12 + (min_salary_amount * 0.12)
            elif employee_finance.epf_type == "2":
                pass
            net_salary = net_salary - epf + total_allowance + attendance_allowance - total_deduction

            
        except EmployeeFinance.DoesNotExist:
            epf_status =  None
            print("Employee Finance Does not exists")
# Calculating Attendance Allowance
        attendance_allowance_26 = 0
        extra_days = 0
        extra_attendance_allowance = 0
        actully_worked_days = len(attendance_record_list)
        worked_days = actully_worked_days + over_night_days
        days_in_month = get_no_of_days_of_the_month(month)
        if worked_days >= 26:
            attendance_allowance_26 = 1000
            attendance_allowance = attendance_allowance + 1000
        if worked_days > 26:
            if worked_days > days_in_month:
                worked_days =  days_in_month
            extra_days = worked_days-26
            extra_attendance_allowance = (worked_days-26)*500
            attendance_allowance = attendance_allowance + (worked_days-26)*500
# Adding Employee Basic Details
        employee = emp

        # Calculate salary if attendance payment is less than fixed payment   
        calculated_fixed_basic_salary =  br_payment + fixed_basic_salary 

        if calculated_fixed_basic_salary > basic_salary:
            br_payment = 140 * worked_days
            fixed_basic_salary = basic_salary - br_payment
            if fixed_basic_salary > 13100.0:
                fixed_allowance =  fixed_basic_salary - 13100.0
                fixed_basic_salary = 13100.0
            else:
                fixed_allowance = 0.0
            
            net_salary = basic_salary + ot_payment - room_charge - total_advance_amount - epf + total_allowance + attendance_allowance - total_deduction
        if worked_days >= 1:

            return [attendance_allowance,fixed_allowance,br_payment,fixed_basic_salary,room_charge,epf,total_advance_amount,total_allowance,ot_payment,ot_payment_rate,hourly_payment_rate,basic_salary,net_salary,attendance_record_list,total_working_hours,total_ot_hours,attendance_allowance_26,extra_days,extra_attendance_allowance,epf_status,actully_worked_days,over_night_days,deductions,total_deduction,epf_12,employee.nic_no,employee.emp_id,employee.name,employee.dprtmnt.department,employee.epf_no,allowances,worked_days]
        else: 
            return[0]
# Salary Calculation for Shift Employees
    elif emp.emp_type == 1:
        attendance_record = Attendance.objects.filter(
                            employee=emp,date__month=month,date__year=year).order_by('date')
        attendance_record_list = list(attendance_record.values())
        employee_finance_record = EmployeeFinance.objects.filter(
                employee=emp,effective_from__month__lte = month,effective_from__year__lte = year).order_by("-effective_from",'-submit_date').first()
    # Checking wether there is a Employee Finance Record    
        if employee_finance_record == None: 
            return "employee_finance_details_error"
        else:
            daily_payment_rate = employee_finance_record.daily_payment
            ot_rate = employee_finance_record.ot_payment_rate
            basic_salary =  employee_finance_record.basic_salary
            br_payment = employee_finance_record.br_payment
            room_charge = employee_finance_record.room_charge
            production_allowance = employee_finance_record.production_allowance
            special_allowance = 0.0
            total_ot_hours = 0.0
            total_advance_amount = 0.0 
            total_deduction = 0.0
            deductions = []
            total_allowance = 0.0 + production_allowance 
            allowances = []
            net_salary = 0.0

            no_of_worked_days = len(attendance_record)

            attendance_allowance =  no_of_worked_days * daily_payment_rate
            if no_of_worked_days >= 18:
                special_allowance += 10000.0
                total_allowance += special_allowance
            else:
                basic_salary_rate =  (basic_salary + br_payment)/18
                basic_salary_total_worked_days =  basic_salary_rate * no_of_worked_days
                br_payment =  140 * no_of_worked_days
                basic_salary = basic_salary_total_worked_days - br_payment
        # Calculating OT
            i = 0
            for record in attendance_record:
                normal_working_hours = 9.0
                date =  record.date
                day = record.day
                date_split = str(date).split('-')
                in_time =  record.in_time
                out_time = record.out_time
                in_time_split = str(in_time).split('.')
                out_time_split = str(out_time).split('.')

                in_time_obj = datetime(int(date_split[0]), int(date_split[1]), int(date_split[2]), int(in_time_split[0]), int(in_time_split[1]))
                out_time_obj = datetime(int(date_split[0]), int(date_split[1]), int(date_split[2]), int(out_time_split[0]), int(out_time_split[1])) 
                attendance_out_time_noon = datetime(int(date_split[0]), int(date_split[1]), int(date_split[2]), 12, 00)
                attendance_out_time_mid_night = datetime(int(date_split[0]), int(date_split[1]), int(date_split[2]), 00, 00)
                
                if record.next_day == True: #In and out in 2 days
                    out_time_obj += + timedelta(days=1)
                    worked_hours = (out_time_obj - in_time_obj).total_seconds()/(60*60)
                else: # In and out in one day
                    worked_hours = (out_time_obj - in_time_obj).total_seconds()/(60*60)
                worked_hours -= 1 #Deducting the lunch hour
            # 1)Calculating OT Hours
                if day == "Sunday" and record.special_holiday == False:
                    ot_hours = worked_hours
                    total_ot_hours += ot_hours
                elif day == "Saturday" and record.special_holiday == False:
                    ot_hours = (worked_hours - 5) if (worked_hours > 5) else 0
                    total_ot_hours += ot_hours
                elif record.special_holiday == True:
                    ot_hours = worked_hours
                    total_ot_hours += ot_hours
                else:
                    ot_hours = (worked_hours - 8) if (worked_hours > 8) else 0
                    total_ot_hours += ot_hours
                attendance_record_list[i]["working_hours"] = worked_hours
                attendance_record_list[i]["ot_hours"] = ot_hours
                i += 1
            # 2)Calculating OT Amount
            ot_payment =  ot_rate * total_ot_hours
        # Calculating Salary Advance
            try:
                advance_payment_data = SalaryAdvance.objects.filter(
                    employee=emp, date__month=month,date__year=year).order_by('date').values()
                advance_payment_data_list = list(advance_payment_data)
                total_advance_amount = 0
                for advance in advance_payment_data_list:
                    total_advance_amount +=  advance["amount"]
                
            except SalaryAdvance.DoesNotExist:
                print("Salary Advances does not exists")
        # Calculating Deductions    
            try:
                deduction_data = Deduction.objects.filter(
                    employee=emp, date__month=month,status =True,date__year=year).order_by('date').values()
                deduction_data_list = list(deduction_data)
                
                
                for deduction in deduction_data_list:
                    deductions.append([deduction["description"],deduction["amount"]])
                    total_deduction +=  deduction["amount"]
            except Deduction.DoesNotExist:
                print("No Deductions")
        # Calculating Allowances     
            try:
                allowance_data = Alllowance.objects.filter(
                    employee=emp, date__month=month,status =True,date__year=year).order_by('date').values()
                allowance_data_list = list(allowance_data)
                
                
                for allowance in allowance_data_list:
                    allowances.append([allowance["description"],allowance["amount"]])
                    total_allowance = total_allowance + allowance["amount"]
            except Alllowance.DoesNotExist:
                print("No Allowance")
        # Calculating EPF 
            total_basic_salary =  basic_salary + br_payment
            epf = total_basic_salary * 0.08
        

        # Calculating Net Salary
            net_salary = basic_salary + br_payment + ot_payment + attendance_allowance  - total_deduction - total_advance_amount - epf - room_charge + total_allowance


            return [attendance_record_list , no_of_worked_days , total_ot_hours , ot_rate , ot_payment , basic_salary, br_payment , attendance_allowance ,total_advance_amount ,total_deduction , deductions , epf , room_charge ,total_allowance , allowances , net_salary , special_allowance , production_allowance , daily_payment_rate]
                






class PayslipInfo(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def get(self,request):
        user = request.user
        return render(request,'payslips.html',context={'user':user})
    def post(self,request):
        # Employee ID and Month
        if request.POST["type"] == "id_month":
            emp_id = request.POST["emp_id"]
            year_month = request.POST["month"]
            emp = Employee.objects.get(emp_id=emp_id)
            year_month_split = year_month.split('-')
            payslips_record = []
            no = 0
            if emp.emp_type == 0:
                try :
                    response = get_final_salary_details(emp,month=year_month_split[1],year=year_month_split[0])
                    print(f"response {response}")
                    if response == "employee_finance_details_error":
                        payslips_record.append({'no':no,'emp_id':emp_id if emp_id[0] == "A" else f"A{emp_id[1::]}","name":emp.name,"month":year_month,"status":2})
                    elif response == "Department Empty":
                        payslips_record.append({'no':no,'emp_id':emp_id if emp_id[0] == "A" else f"A{emp_id[1::]}","name":emp.name,"month":year_month,"status":3})
                    else:
                        payslips_record.append({'no':no,'emp_id':emp_id if emp_id[0] == "A" else f"A{emp_id[1::]}","name":emp.name,"month":year_month,"status":0})
                    return JsonResponse({"data":payslips_record})
                except (ValueError,IndexError):
                    payslips_record.append({'no':no,'emp_id':emp_id if emp_id[0] == "A" else f"A{emp_id[1::]}","name":emp.name,"month":year_month,"status":1})
                except(AttributeError):
                    print("cought")
                    payslips_record.append({'no':no,'emp_id':emp_id if emp_id[0] == "A" else f"A{emp_id[1::]}","name":emp.name,"month":year_month,"status":4})
            elif emp.emp_type == 1:
                try :
                    response = get_final_salary_details(emp,month=year_month_split[1],year=year_month_split[0])
                    if response == "employee_finance_details_error":
                        payslips_record.append({'no':no,'emp_id':emp_id if emp_id[0] == "A" else f"A{emp_id[1::]}","name":emp.name,"month":year_month,"status":2})
                    elif response[1] == 0:
                        pass
                    else:
                        payslips_record.append({'no':no,'emp_id':emp_id if emp_id[0] == "A" else f"A{emp_id[1::]}","name":emp.name,"month":year_month,"status":0})
                except(ValueError,IndexError):
                    payslips_record.append({'no':no,'emp_id':emp_id if emp_id[0] == "A" else f"A{emp_id[1::]}","name":emp.name,"month":year_month,"status":1})
            return JsonResponse({"data":payslips_record})
        elif request.POST["type"] == "month":
            year_month = request.POST["month"]
            emp_type = request.POST["emp_type"]
            year_month_split = year_month.split('-')
            payslips_record = []
            if emp_type == "0":
                employees = Employee.objects.filter(emp_type=0)
                employees_list = list(employees)
                no = 1
                for employee in employees_list:
                    emp_id = employee.emp_id
                    try :

                        response = get_final_salary_details(employee,month=year_month_split[1],year=year_month_split[0])
                        if employee.active_status == 0 and (response == "employee_finance_details_error" or response == "Department Empty"): 
                            pass
                        elif response == "employee_finance_details_error" and employee.active_status == 1:
                            payslips_record.append({'no':no,'emp_id':emp_id if emp_id[0] == "A" else f"A{emp_id[1::]}","name":employee.name,"month":year_month,"status":2})
                            no += 1
                        elif response == "Department Empty" and employee.active_status == 1:
                            payslips_record.append({'no':no,'emp_id':emp_id if emp_id[0] == "A" else f"A{emp_id[1::]}","name":employee.name,"month":year_month,"status":3})
                            no += 1
                        elif response[-1] == 0: # Ignoring Employees Who haven't worked for atleast 1 day
                            pass
                        else:
                            payslips_record.append({'no':no,'emp_id':emp_id if emp_id[0] == "A" else f"A{emp_id[1::]}","name":employee.name,"month":year_month,"status":0})
                            no += 1
                    except (ValueError,IndexError):
                        payslips_record.append({'no':no,'emp_id':emp_id if emp_id[0] == "A" else f"A{emp_id[1::]}","name":employee.name,"month":year_month,"status":1})
                        no += 1
            elif emp_type == "1":
                employees = Employee.objects.filter(emp_type=1)
                employees_list = list(employees)
                no = 1
                for employee in employees_list:
                    emp_id = employee.emp_id
                    try :
                        response = get_final_salary_details(employee,month=year_month_split[1],year=year_month_split[0])
                        if employee.active_status == 0:
                            pass
                        elif response == "employee_finance_details_error":
                            payslips_record.append({'no':no,'emp_id':emp_id if emp_id[0] == "A" else f"A{emp_id[1::]}","name":employee.name,"month":year_month,"status":2})
                            no += 1
                        elif response[1] == 0:
                            pass
                        else:
                            payslips_record.append({'no':no,'emp_id':emp_id if emp_id[0] == "A" else f"A{emp_id[1::]}","name":employee.name,"month":year_month,"status":0})
                            no += 1
                    except (ValueError,IndexError):
                        payslips_record.append({'no':no,'emp_id':emp_id if emp_id[0] == "A" else f"A{emp_id[1::]}","name":employee.name,"month":year_month,"status":1})
                        no += 1
            return JsonResponse({"data":payslips_record})

            
class PayslipPdfView(LoginRequiredMixin,View):

    login_url = '/accounts/login'
    def post(self,request):

        emp_ids = request.POST["emp_ids"]
        emp_ids_list = emp_ids.split(',')

        # emp_id = request.POST["emp_id"]
        year_month = request.POST["payslip_month"]
        year_month_split = year_month.split('-')
        emp_type = request.POST["payslip_emp_type"]

        if len(emp_ids_list) == 1:
            emp = Employee.objects.get(emp_id=emp_ids_list[0])
            response = get_final_salary_details(emp,month=year_month_split[1],year=year_month_split[0])
            if emp.emp_type == 0:
                buffer = io.BytesIO()

                pdf = canvas.Canvas(buffer,pagesize = landscape(A4))
                
                # pdf = canvas.Canvas(filename="test.pdf",pagesize = landscape(A4))

                flow_obj = []

                company_name = "Ceylon Marine Services Holdings (Pvt)Ltd"
                month = year_month
                employee_name = emp.name
                department = emp.dprtmnt.department
                if len(department) >= 12 or len(employee_name) >= 12:
                    font_size = 6.0
                else:
                    font_size = 6.0
                epf_no = response[-3]
                employee_no =response[-6] if (response[-6])[0] == "A" else f"A{(response[-6])[1::-1]}"
                basic_salary =response[3]
                br_payment=response[2]
                fixed_allowance = response[1]
                gross_salary = basic_salary+ br_payment +fixed_allowance
                ot_payment = response[8]
                ot_payment_rate = response[9]
                ot_hours= response[15]
                total_allowance = response[7]
                total_deduction = response[-9]
                epf=response[5]
                salary_advance = response[6]
                room_charge = response[4]
                total_deduction = epf + salary_advance + room_charge + total_deduction
                net_payment=response[12]
                attendance_allowance_26 = response[16]
                extra_days = response[17]
                extra_payment = response[18]
                total_earning = ot_payment + attendance_allowance_26 + extra_payment + total_allowance +basic_salary + br_payment +fixed_allowance
                total_worked_days = response[-1]

                table_data = []
                # op, start, stop, weight, colour, cap, dashes, join, linecount, linespacing
                row1 = [company_name]
                row2 = [month]
                empty_row1 = [""]
                row3 = ["Employee Name :","",employee_name,""]
                row4 = ["Department","",department,""]
                row5 = ["Employee No:","",employee_no]
                row6 = ["E.P.F No","",epf_no]
                empty_row5 = [""]
                row7 = ["Basic Salary","",f"{basic_salary:>9.2f}",""]
                row8 = ["B R Allowance","",f"{br_payment:>9.2f}",""]
                row9 = ["Other Allowance","",f"{fixed_allowance:>9.2f}",""]
                # row10 = ["Gross Salary","","",f"{gross_salary:>9.2f}"]
                empty_row2 = [""]
                row11 = ["Additions","","",""]
                row12 = [f"OT({ot_payment_rate} x {ot_hours} Hrs)","",f"{ot_payment:>9.2f}",""]
                row13 =  [f"Att Allowance 26 days ","",f"{attendance_allowance_26:>9.2f}"]
                row131 = [f"Att Allowance Extra {extra_days} x 500  ","",f"{extra_payment:>9.2f}"]
                # row132 = [f"Other Allowances ","",f"{total_allowance:>9.2f}"]
                row14 = ["Total Earning","","",f"{total_earning:>9.2f}"]
                empty_row3 = [""]
                row15 = ["Deductions","","",""]
                row16 = ["EPF 8%","",f"{epf:9.2f}",""]
                row17 = ["Salary Advance","",f"{salary_advance:9.2f}",""]
                row18 = ["Room Charges","",f"{room_charge:9.2f}",""]
                row19 = ["Total Deductions","","",f"{total_deduction:9.2f}"]
                empty_row4 = [""]
                row20 = ["Net Payment","","",f"{net_payment:9.2f}"]
                row21 = ["Total OT Hours","",f"{ot_hours:>9} Hrs",""]
                row22 = ["Total Worked Days","",f"{total_worked_days:>9} Days",""]
                deduction_line = -9
                table_data.append(row1)
                table_data.append(row2)
                table_data.append(empty_row1)
                table_data.append(row3)
                table_data.append(row4)
                table_data.append(row5)
                table_data.append(row6)
                table_data.append(empty_row5)

                table_data.append(row7)
                table_data.append(row8)
                table_data.append(row9)
                # table_data.append(row10)
                table_data.append(empty_row2)
                table_data.append(row11)
                table_data.append(row12)
                table_data.append(row13)
                table_data.append(row131)
                for allowance in response[-2]:
                    table_data.append([f"{allowance[0]} ","",f"{allowance[1]:>9.2f}"])
                # table_data.append(row132)
                table_data.append(row14)
                table_data.append(empty_row3)
                table_data.append(row15)
                table_data.append(row16)
                table_data.append(row17)
                for deduction in response[-10]:
                    deduction_line += -1
                    table_data.append([f"{deduction[0]} ","",f"{deduction[1]:>9.2f}"])
                table_data.append(row18)
                table_data.append(row19)
                table_data.append(empty_row4)
                table_data.append(row20)
                table_data.append(row21)
                table_data.append(row22)


                print(deduction_line)
                table = Table(table_data,colWidths=[1.35*inch,0*inch,0.8*inch,0.55*inch])
                table_style = TableStyle([
                    # ("GRID",(0,0),(-1,-1),1,colors.black),
                    ('FONT', (0, 0), (-1, -1), 'Helvetica',7.0),
                    ('BOLD', (0, 0), (-1, -1)),
                    
                    ('SPAN', (0, 0), (-1, 0)), # Company Name Row
                    ('SPAN', (0, 1), (-1,1 )), # Month Row
                    ('SPAN', (0, 3), (1,3 )), # Name Column 
                    ('SPAN', (2, 3), (3,3 )), # Department Column 
                    ('SPAN', (0, 6), (1,6 )), # Employee No Cell 
                    ('SPAN', (2, 6), (3,6 )), # EPF No Cell 
                    ('ALIGN', (0, 0), (-1, 1),'CENTER'),
                    ('ALIGN', (2, 8), (-1, -1),'RIGHT'),
                    ('LINEABOVE', (0, 8), (-1, 8),1,colors.black),
                    ('LINEBELOW', (0, 12), (0, 12),1,colors.black),
                    ('LINEBELOW', (0, deduction_line), (0, deduction_line),1,colors.black),
                    # ('LINEBELOW', (2, 10), (3, 10),1,colors.black),
                    ('LINEBELOW', (2, -13), (3, -13),1,colors.black),
                    ('LINEBELOW', (2, -6), (3,-6),1,colors.black),
                    ('LINEBELOW', (0, -3), (-1, -3),1,colors.black),
                    ('LINEBELOW', (0, -1), (-1, -1),1,colors.black),
                    ('LINEAFTER', (1, 8), (1, -1),1,colors.black),
                ])
                table.setStyle(table_style)
                flow_obj.append(table)
                frame1 = Frame(0.35*cm,0.5*cm,7*cm,20*cm,showBoundary=1)
                frame1.addFromList(flow_obj,pdf)
                pdf.setTitle(f"{emp.emp_id}-{employee_name}-{month}-Salary Slip")
                pdf.save()
                buffer.seek(0)
                return FileResponse(buffer, as_attachment=True, filename=f"{emp.emp_id}-{employee_name}-{month}-payslip.pdf")
            elif emp.emp_type == 1:
                buffer = io.BytesIO()
                pdf = canvas.Canvas(buffer,pagesize = landscape(A4))
                flow_obj = []

                company_name = "Ceylon Marine Services Holdings (Pvt)Ltd"
                month = year_month
                employee_name = emp.name
                department = emp.dprtmnt
                epf_no = emp.epf_no
                employee_no =emp.emp_id if (emp.emp_id)[0] == "A" else f"A{(emp.emp_id)[1::-1]}"
                fixed_basic_salary =response[5]
                br_payment=response[6]
                basic_salary = fixed_basic_salary + br_payment
                special_allowance = response[16]
                production_allowance = response[17]
                attendance_allowance =  response[7]
                ot_payment = response[4]
                ot_payment_rate = response[3]
                ot_hours= response[2]
                total_allowance = response[13]
                allowances =  response[14]
                gross_salary = basic_salary + special_allowance + production_allowance + attendance_allowance + ot_payment + total_allowance
                epf=response[11]
                salary_advance = response[8]
                room_charge = response[12]
                deductions = response[10]
                other_total_deductions =  response[9]
                total_deduction = epf + salary_advance + room_charge + other_total_deductions
                net_salary = response[15]
                attendance_allowance_per_day =  response[18]
                total_worked_days = response[1]

                table_data = []
                # op, start, stop, weight, colour, cap, dashes, join, linecount, linespacing
                row1 = [company_name]
                row2 = [month]
                empty_row1 = [""]
                row3 = ["Employee Name :","",employee_name,""]
                row4 = ["Department","",department,""]
                row5 = ["Employee No:","",employee_no]
                row6 = ["E.P.F No","",epf_no]
                empty_row5 = [""]
                row7 = ["Basic Salary","",f"{basic_salary:>9.2f}",""]
                row8 = ["Special Allowance","",f"{special_allowance:>9.2f}",""]
                row9 = ["Production Allowance","",f"{production_allowance:>9.2f}",""]
                # row10 = ["Gross Salary","","",f"{gross_salary:>9.2f}"]
                empty_row2 = [""]
                row11 = ["Additions","","",""]
                row12 = [f"OT({ot_payment_rate} x {ot_hours} Hrs)","",f"{ot_payment:>9.2f}",""]
                row13 =  [f"Att Allowance 26 days ","",f"{ot_payment:>9.2f}"]
                row131 = [f"Att Allowance Extra {total_worked_days} x 500  ","",f"{ot_payment:>9.2f}"]
                # row132 = [f"Other Allowances ","",f"{total_allowance:>9.2f}"]
                row14 = ["Total Earning","","",f"{ot_payment:>9.2f}"]
                empty_row3 = [""]
                row15 = ["Deductions","","",""]
                row16 = ["EPF 8%","",f"{epf:9.2f}",""]
                row17 = ["Salary Advance","",f"{salary_advance:9.2f}",""]
                row18 = ["Room Charges","",f"{room_charge:9.2f}",""]
                row19 = ["Total Deductions","","",f"{total_deduction:9.2f}"]
                empty_row4 = [""]
                row20 = ["Net Payment","","",f"{net_salary:9.2f}"]
                row21 = ["Total OT Hours","",f"{ot_hours:>9} Hrs",""]
                row22 = ["Total Worked Days","",f"{total_worked_days:>9} Days",""]
                deduction_line = -9
                table_data.append(row1)
                table_data.append(row2)
                table_data.append(empty_row1)
                table_data.append(row3)
                table_data.append(row4)
                table_data.append(row5)
                table_data.append(row6)
                table_data.append(empty_row5)

                table_data.append(row7)
                table_data.append(row8)
                table_data.append(row9)
                # table_data.append(row10)
                table_data.append(empty_row2)
                table_data.append(row11)
                table_data.append(row12)
                table_data.append(row13)
                table_data.append(row131)
                for allowance in response[-2]:
                    table_data.append([f"{allowance[0]} ","",f"{allowance[1]:>9.2f}"])
                # table_data.append(row132)
                table_data.append(row14)
                table_data.append(empty_row3)
                table_data.append(row15)
                table_data.append(row16)
                table_data.append(row17)
                for deduction in response[-10]:
                    deduction_line += -1
                    table_data.append([f"{deduction[0]} ","",f"{deduction[1]:>9.2f}"])
                table_data.append(row18)
                table_data.append(row19)
                table_data.append(empty_row4)
                table_data.append(row20)
                table_data.append(row21)
                table_data.append(row22)


                print(deduction_line)
                table = Table(table_data,colWidths=[1.35*inch,0*inch,0.8*inch,0.55*inch])
                table_style = TableStyle([
                    # ("GRID",(0,0),(-1,-1),1,colors.black),
                    ('FONT', (0, 0), (-1, -1), 'Helvetica',7.0),
                    ('BOLD', (0, 0), (-1, -1)),
                    
                    ('SPAN', (0, 0), (-1, 0)), # Company Name Row
                    ('SPAN', (0, 1), (-1,1 )), # Month Row
                    ('SPAN', (0, 3), (1,3 )), # Name Column 
                    ('SPAN', (2, 3), (3,3 )), # Department Column 
                    ('SPAN', (0, 6), (1,6 )), # Employee No Cell 
                    ('SPAN', (2, 6), (3,6 )), # EPF No Cell 
                    ('ALIGN', (0, 0), (-1, 1),'CENTER'),
                    ('ALIGN', (2, 8), (-1, -1),'RIGHT'),
                    ('LINEABOVE', (0, 8), (-1, 8),1,colors.black),
                    ('LINEBELOW', (0, 12), (0, 12),1,colors.black),
                    ('LINEBELOW', (0, deduction_line), (0, deduction_line),1,colors.black),
                    # ('LINEBELOW', (2, 10), (3, 10),1,colors.black),
                    ('LINEBELOW', (2, -13), (3, -13),1,colors.black),
                    ('LINEBELOW', (2, -6), (3,-6),1,colors.black),
                    ('LINEBELOW', (0, -3), (-1, -3),1,colors.black),
                    ('LINEBELOW', (0, -1), (-1, -1),1,colors.black),
                    ('LINEAFTER', (1, 8), (1, -1),1,colors.black),
                ])
                table.setStyle(table_style)
                flow_obj.append(table)
                frame1 = Frame(0.35*cm,0.5*cm,7*cm,20*cm,showBoundary=1)
                frame1.addFromList(flow_obj,pdf)
                pdf.setTitle(f"{emp.emp_id}-{employee_name}-{month}-Salary Slip")
                pdf.save()
                buffer.seek(0)
                return FileResponse(buffer, as_attachment=True, filename=f"{emp.emp_id}-{employee_name}-{month}-payslip.pdf")
        elif len(emp_ids_list) > 1:
            if emp_type == "0":
                payslips_record = []
                employees = Employee.objects.filter(emp_id__in=emp_ids_list)
                for employee in employees:
                    try :
                        response = get_final_salary_details(employee,month=year_month_split[1],year=year_month_split[0])
                        if response == "employee_finance_details_error" or response == "Department Empty":
                            pass
                        elif response[-1] == 0:
                            pass
                        else:
                            payslips_record.append(response)
                    except (ValueError,IndexError):
                        pass
                buffer = io.BytesIO()
                pdf = canvas.Canvas(buffer,pagesize = landscape(A4))
                # pdf = canvas.Canvas(filename="testtttt.pdf",pagesize = landscape(A4))
                company_name = "Ceylon Marine Services Holdings (Pvt)Ltd"
                month = year_month
                
                frames = [(0.35,0.5,7,20),(7.68,0.5,7,20),(15.01,0.5,7,20),(22.34,0.5,7,20)]

                # Calculating No of Pages
                data_length = len(payslips_record)
                frame_names = [f"frame{i}"for i in range(len(payslips_record))]
                no_pages = 0
                if data_length == 4:
                    no_pages = 1
                elif data_length < 4:
                    no_pages = 1
                elif data_length > 4:
                    no_pages = (data_length // 4) + 1

                i = 0
                k=0
                j=0
                frame_list = []
                for frame in frame_names:
                    if i <= no_pages:
                        if j < 4:
                            frame_list.append(Frame(frames[j][0]*cm,frames[j][1]*cm,frames[j][2]*cm,frames[j][3]*cm,showBoundary=1))
                            j += 1
                            
                            if j == 4:
                                j=0
                                i += 1  
                            print(j)
                            

                    k += 1  
                i = 0
                k=0
                j=0
                flow_obj = []
                for response in payslips_record:
                    employee_name = response[-5]
                    department =  response[-4]
                    if len(department) >= 12 or len(employee_name) >= 12:
                        font_size = 6.0
                    else:
                        font_size = 6.0
                    epf_no = response[-3]
                    employee_no =response[-6] if (response[-6])[0] == "A" else f"A{(response[-6])[1::]}"
                    basic_salary =response[3]
                    br_payment=response[2]
                    fixed_allowance = response[1]
                    gross_salary = basic_salary+ br_payment +fixed_allowance
                    ot_payment = response[8]
                    ot_payment_rate = response[9]
                    ot_hours= response[15]
                    total_allowance = response[7]
                    total_deduction = response[-9]
                    epf=response[5]
                    salary_advance = response[6]
                    room_charge = response[4]
                    total_deduction = epf + salary_advance + room_charge + total_deduction
                    net_payment=response[12]
                    attendance_allowance_26 = response[16]
                    extra_days = response[17]
                    extra_payment = response[18]
                    total_earning = ot_payment + attendance_allowance_26 + extra_payment + total_allowance +basic_salary + br_payment +fixed_allowance
                    total_worked_days = response[-1]

                    table_data = []
                    # op, start, stop, weight, colour, cap, dashes, join, linecount, linespacing
                    row1 = [company_name]
                    row2 = [month]
                    empty_row1 = [""]
                    row3 = ["Employee Name :","",employee_name,""]
                    row4 = ["Department","",department,""]
                    row5 = ["Employee No:","",employee_no]
                    row6 = ["E.P.F No","",epf_no]
                    empty_row5 = [""]
                    row7 = ["Basic Salary","",f"{basic_salary:>9.2f}",""]
                    row8 = ["B R Allowance","",f"{br_payment:>9.2f}",""]
                    row9 = ["Other Allowance","",f"{fixed_allowance:>9.2f}",""]
                    # row10 = ["Gross Salary","","",f"{gross_salary:>9.2f}"]
                    empty_row2 = [""]
                    row11 = ["Additions","","",""]
                    row12 = [f"OT ({ot_payment_rate} x {ot_hours} Hrs)","",f"{ot_payment:>9.2f}",""]
                    row13 =  [f"Att Allowance 26 days","",f"{attendance_allowance_26:>9.2f}"]
                    row131 = [f"Att Allowance Extra {extra_days} x 500  ","",f"{extra_payment:>9.2f}"]
                    # row132 = [f"Other Allowances ","",f"{total_allowance:>9.2f}"]
                    row14 = ["Total Earning","","",f"{total_earning:>9.2f}"]
                    empty_row3 = [""]
                    row15 = ["Deductions","","",""]
                    row16 = ["EPF 8%","",f"{epf:9.2f}",""]
                    row17 = ["Salary Advance","",f"{salary_advance:9.2f}",""]
                    row18 = ["Room Charges","",f"{room_charge:9.2f}",""]
                    row19 = ["Total Deductions","","",f"{total_deduction:9.2f}"]
                    empty_row4 = [""]
                    row20 = ["Net Payment","","",f"{net_payment:9.2f}"]
                    row21 = ["Total OT Hours","",f"{ot_hours:>9} Hrs",""]
                    row22 = ["Total Worked Days","",f"{total_worked_days:>9} Days",""]

                    deduction_line = -9
                    table_data.append(row1)
                    table_data.append(row2)
                    table_data.append(empty_row1)
                    table_data.append(row3)
                    table_data.append(row4)
                    table_data.append(row5)
                    table_data.append(row6)
                    table_data.append(empty_row5)

                    table_data.append(row7)
                    table_data.append(row8)
                    table_data.append(row9)
                    # table_data.append(row10)
                    table_data.append(empty_row2)
                    table_data.append(row11)
                    table_data.append(row12)
                    table_data.append(row13)
                    table_data.append(row131)
                    for allowance in response[-2]:
                        table_data.append([f"{allowance[0]} ","",f"{allowance[1]:>9.2f}"])
                    # table_data.append(row132)
                    table_data.append(row14)
                    table_data.append(empty_row3)
                    table_data.append(row15)
                    table_data.append(row16)
                    table_data.append(row17)
                    for deduction in response[-10]:
                        deduction_line += -1
                        table_data.append([f"{deduction[0]} ","",f"{deduction[1]:>9.2f}"])
                    table_data.append(row18)
                    table_data.append(row19)
                    table_data.append(empty_row4)
                    table_data.append(row20)
                    table_data.append(row21)
                    table_data.append(row22)



                    table = Table(table_data,colWidths=[1.35*inch,0*inch,0.8*inch,0.55*inch])
                    table_style = TableStyle([
                        # ("GRID",(0,0),(-1,-1),1,colors.black),
                        ('FONT', (0, 0), (-1, -1), 'Helvetica',7.0),
                        ('BOLD', (0, 0), (-1, -1)),

                        ('SPAN', (0, 0), (-1, 0)), # Company Name Row
                        ('SPAN', (0, 1), (-1,1 )), # Month Row
                        ('SPAN', (0, 3), (1,3 )), # Name Column 
                        ('SPAN', (2, 3), (3,3 )), # Department Column 
                        ('SPAN', (0, 6), (1,6 )), # Employee No Cell 
                        ('SPAN', (2, 6), (3,6 )), # EPF No Cell 
                        ('ALIGN', (0, 0), (-1, 1),'CENTER'),
                        ('ALIGN', (2, 8), (-1, -1),'RIGHT'),
                        ('LINEABOVE', (0, 8), (-1, 8),1,colors.black),
                        ('LINEBELOW', (0, 12), (0, 12),1,colors.black),
                        ('LINEBELOW', (0, deduction_line), (0, deduction_line),1,colors.black),
                        # ('LINEBELOW', (2, 10), (3, 10),1,colors.black),
                        ('LINEBELOW', (2, -12), (3, -12),1,colors.black),
                        ('LINEBELOW', (2, -6), (3,-6),1,colors.black),
                        ('LINEBELOW', (0, -3), (-1, -3),1,colors.black),
                        ('LINEBELOW', (0, -1), (-1, -1),1,colors.black),
                        ('LINEAFTER', (1, 8), (1, -1),1,colors.black),


                    ])
                    table.setStyle(table_style)
                    flow_obj.append(table)
                    print(j)
                    frame_list[k].addFromList(flow_obj,pdf)
                    j += 1
                    if j == 4:
                        flow_obj = []
                        j=0
                        i += 1  
                        pdf.showPage()    
                    k += 1
                pdf.save()
                pdf.setTitle(f"{month}-Salary Slips")
                buffer.seek(0)   
                print("end")
                return FileResponse(buffer, as_attachment=True, filename=f"payslip.pdf")
            elif emp_type == "1":
                payslips_record = []
                employees = Employee.objects.filter(emp_id__in=emp_ids_list)
                for employee in employees:
                    try :
                        response = get_final_salary_details(employee,month=year_month_split[1],year=year_month_split[0])
                        if response == "employee_finance_details_error":
                            pass
                        elif response[1] == 0:
                            pass
                        else:
                            payslips_record.append([employee,response])
                    except (ValueError,IndexError):
                        pass
                buffer = io.BytesIO()
                pdf = canvas.Canvas(buffer,pagesize = landscape(A4))
                # pdf = canvas.Canvas(filename="testtttt.pdf",pagesize = landscape(A4))
                company_name = "Ceylon Marine Services Holdings (Pvt)Ltd"
                month = year_month
                
                frames = [(0.35,0.5,7,20),(7.68,0.5,7,20),(15.01,0.5,7,20),(22.34,0.5,7,20)]

                # Calculating No of Pages
                data_length = len(payslips_record)
                frame_names = [f"frame{i}"for i in range(len(payslips_record))]
                no_pages = 0
                if data_length == 4:
                    no_pages = 1
                elif data_length < 4:
                    no_pages = 1
                elif data_length > 4:
                    no_pages = (data_length // 4) + 1

                i = 0
                k=0
                j=0
                frame_list = []
                for frame in frame_names:
                    if i <= no_pages:
                        if j < 4:
                            frame_list.append(Frame(frames[j][0]*cm,frames[j][1]*cm,frames[j][2]*cm,frames[j][3]*cm,showBoundary=1))
                            j += 1
                            
                            if j == 4:
                                j=0
                                i += 1  
                            

                    k += 1  
                i = 0
                k=0
                j=0
                flow_obj = []
                for record in payslips_record:
                    employee_name = record[0].name
                    department = record[0].dprtmnt
                    epf_no = record[0].epf_no
                    employee_no =record[0].emp_id if (record[0].emp_id)[0] == "A" else f"A{(record[0].emp_id)[1::-1]}"
                    fixed_basic_salary =record[1][5]
                    br_payment=record[1][6]
                    basic_salary = fixed_basic_salary + br_payment
                    special_allowance = record[1][16]
                    production_allowance = record[1][17]
                    attendance_allowance =  record[1][7]
                    ot_payment = record[1][4]
                    ot_payment_rate = record[1][3]
                    ot_hours= record[1][2]
                    total_allowance = record[1][13]
                    allowances =  record[1][14]
                    gross_salary = basic_salary +  production_allowance + attendance_allowance + ot_payment + total_allowance
                    epf=record[1][11]
                    salary_advance = record[1][8]
                    room_charge = record[1][12]
                    deductions = record[1][10]
                    other_total_deductions =  record[1][9]
                    total_deduction = epf + salary_advance + room_charge + other_total_deductions
                    net_salary = record[1][15]
                    attendance_allowance_per_day =  record[1][18]
                    total_worked_days = record[1][1]

                    table_data = []
                    # op, start, stop, weight, colour, cap, dashes, join, linecount, linespacing
                    row1 = [company_name]
                    row2 = [month]
                    empty_row1 = [""]
                    row3 = ["Employee Name :","",employee_name,""]
                    row4 = ["Department","",department,""]
                    row5 = ["Employee No:","",employee_no]
                    row6 = ["E.P.F No","",epf_no]
                    row_empty = [""]
                    empty_row5 = ["Earnings","","",""]
                    row7 = ["Basic Salary","",f"{basic_salary:>9,.2f}",""]
                    row8 = ["Special Allowance","",f"{special_allowance:>9,.2f}",""]
                    row9 = ["Production Allowance","",f"{production_allowance:>9,.2f}",""]
                    row10 = ["Attendance Allowance","",f"{attendance_allowance:>9,.2f}",""]
                    row11 = [f"OT ({ot_payment_rate} x {ot_hours} Hrs)","",f"{ot_payment:>9,.2f}",""]
                    row12 = ["Gross Salary","","",f"{gross_salary:>9,.2f}"]
                    empty_row3 = [""]
                    row15 = ["Deductions","","",""]
                    row16 = ["EPF 8%","",f"{epf:9.2f}",""]
                    row17 = ["Salary Advance","",f"{salary_advance:9,.2f}",""]
                    row18 = ["Room Charges","",f"{room_charge:9,.2f}",""]
                    row19 = ["Total Deductions","","",f"{total_deduction:9,.2f}"]
                    empty_row4 = [""]
                    row20 = ["Net Salary","","",f"{net_salary:9,.2f}"]
                    row21 = ["Total OT Hours","",f"{ot_hours:>9} Hrs",""]
                    row22 = ["OT Payment Rate","",f"{ot_payment_rate:>9} ",""]
                    row23 = ["Total Worked Days","",f"{total_worked_days:>9} Days",""]
                    row24 = ["Att Allowance per Day","",f"{ot_hours:>9}",""]

                    deduction_line = -11 if room_charge != 0 else -10
                    table_data.append(row1)
                    table_data.append(row2)
                    table_data.append(empty_row1)
                    table_data.append(row3)
                    table_data.append(row4)
                    table_data.append(row5)
                    table_data.append(row6)
                    table_data.append(row_empty)
                    table_data.append(empty_row5)

                    table_data.append(row7)
                    table_data.append(row8)
                    table_data.append(row9)
                    table_data.append(row10)
                    # table_data.append(empty_row2)
                    table_data.append(row11)
                    for allowance in allowances:
                        table_data.append([f"{allowance[0]} ","",f"{allowance[1]:>9.2f}"])
                    table_data.append(row12)
                    table_data.append(empty_row3)
                    table_data.append(row15)
                    table_data.append(row16)
                    table_data.append(row17)
                    for deduction in deductions:
                        deduction_line += -1
                        table_data.append([f"{deduction[0]} ","",f"{deduction[1]:>9.2f}"])
                    if room_charge != 0:
                        table_data.append(row18)
                    table_data.append(row19)
                    table_data.append(empty_row4)
                    table_data.append(row20)
                    table_data.append(row21)
                    table_data.append(row22)
                    table_data.append(row23)
                    table_data.append(row24)



                    table = Table(table_data,colWidths=[1.35*inch,0*inch,0.8*inch,0.55*inch])
                    table_style = TableStyle([
                        # ("GRID",(0,0),(-1,-1),1,colors.black),
                        ('FONT', (0, 0), (-1, -1), 'Helvetica',7.0),
                        ('FONT', (0, 0), (-1, 1), 'Helvetica-Bold',7.0),
                        ('FONT', (0, 3), (0, 6), 'Helvetica-Bold',7.0),
                        ('FONT', (0, 8), (0, 8), 'Helvetica-Bold',7.0),
                        ('FONT', (0, deduction_line), (0, deduction_line), 'Helvetica-Bold',7.0),
                        ('FONT', (0, -12), (-1, -12), 'Helvetica-Bold',7.0), # Gross Salary
                        ('FONT', (0, -5), (-1, -5), 'Helvetica-Bold',7.0), #Net Salary
                        ('FONT', (0, -7), (-1, -7), 'Helvetica-Bold',7.0), #Total Deduction
                        ('BOLD', (0, 0), (-1, -1)),

                        ('SPAN', (0, 0), (-1, 0)), # Company Name Row
                        ('SPAN', (0, 1), (-1,1 )), # Month Row
                        ('SPAN', (0, 3), (1,3 )), # Name Column 
                        ('SPAN', (2, 3), (3,3 )), # Department Column 
                        ('SPAN', (0, 6), (1,6 )), # Employee No Cell 
                        ('SPAN', (2, 6), (3,6 )), # EPF No Cell 
                        ('ALIGN', (0, 0), (-1, 1),'CENTER'),
                        ('ALIGN', (2, 8), (-1, -1),'RIGHT'),
                        ('LINEABOVE', (0, 7), (-1, 7),1,colors.black), # First Devision Line
                        ('LINEBELOW', (0, 8), (0, 8),1,colors.black), # Earnings
                        # ('LINEBELOW', (0, 12), (0, 12),1,colors.black),
                        ('LINEBELOW', (0, deduction_line), (0, deduction_line),1,colors.black),
                        # ('LINEBELOW', (2, 10), (3, 10),1,colors.black),
                        ('LINEBELOW', (2, -13), (3, -13),1,colors.black),
                        ('LINEBELOW', (2, -8), (3,-8),1,colors.black),
                        ('LINEBELOW', (0, -5), (-1, -5),1,colors.black),
                        ('LINEBELOW', (0, -1), (-1, -1),1,colors.black),
                        ('LINEAFTER', (1, 7), (1, -1),1,colors.black),


                    ])
                    table.setStyle(table_style)
                    flow_obj.append(table)
                    print(j)
                    frame_list[k].addFromList(flow_obj,pdf)
                    j += 1
                    if j == 4:
                        flow_obj = []
                        j=0
                        i += 1  
                        pdf.showPage()    
                    k += 1
                pdf.save()
                pdf.setTitle(f"{month}-Salary Slips")
                buffer.seek(0)   
                print("end")
                return FileResponse(buffer, as_attachment=True, filename=f"payslip.pdf")
class DeductionsView(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def get(self,request):
        user = request.user
        return render(request,'deductions.html',context={'user':user})
    
    def post(self,request):
        emp_id = request.POST['emp_id']
        date = request.POST['date']
        amount = request.POST['amount']
        description = request.POST['description']
        emp = Employee.objects.get(emp_id=emp_id)
        time_stamp = datetime.now()

        deduction = Deduction(
            employee=emp, date=date,description=description, amount=amount, time_stamp=time_stamp)
        deduction.save()
        return  JsonResponse({})     
class GetDeductionData(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def post(self,request):
        emp_id = request.POST['emp_id']
        emp = Employee.objects.get(emp_id=emp_id)
        deduction_data = Deduction.objects.filter(
            employee=emp).order_by('date').values()
        deduction_data_list = list(deduction_data)
        return JsonResponse({'deduction_data_list': deduction_data_list})   
    
class EditDeduction(LoginRequiredMixin,View):
    def post(self,request):
        emp_id = request.POST['emp_id']
        date = request.POST['date']
        amount = request.POST['amount']
        description = request.POST['description']
        status = request.POST['status']
        id = request.POST["id"]
        emp = Employee.objects.get(emp_id=emp_id)
        time_stamp = datetime.now()

        deduction_record = Deduction.objects.get(
            employee=emp, id=id)
        deduction_record.date = date
        deduction_record.amount=amount
        deduction_record.description=description
        deduction_record.status= (True if status == "true" else False)
        deduction_record.time_stamp = time_stamp
        deduction_record.save()
        return JsonResponse({})

class AllowancesView(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def get(self,request):
        user = request.user
        return render(request,'allowances.html',context={'user':user})

    def post(self,request):
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
        emp = Employee.objects.get(emp_id = emp_id)
        year_month = request.POST["month"]
        year_month_split = year_month.split('-')
        month = year_month_split[1]

        
# Formating Values
        response = get_final_salary_details(emp,month=month,year=year_month_split[0])
        if response == "employee_finance_details_error":
            return JsonResponse({'error':"no employee finance data"})
        elif response == "Department Empty":
            return JsonResponse({'error':"Department"})
        else:
            if emp.emp_type == 0:
                attendance_record_list = response[13]
                total_working_hours = response[14]
                total_ot_hours = response[15]
                attendance_allowance = response[16] + response[18]
                attendance_allowance_final = "{:>9,.2f}".format(attendance_allowance)
                other_allowance = "{:>9,.2f}".format(response[1])
                br_payment = "{:>9,.2f}".format(response[2])
                fixed_basic_salary = "{:>9,.2f}".format(response[3])
                room_charge = "{:>9,.2f}".format(response[4])
                epf = "{:>9.2f}".format(response[5])
                total_advance_amount = "{:>9,.2f}".format(response[6])
                total_allowance = "{:>9,.2f}".format(response[7])
                total_deduction = "{:>9,.2f}".format(response[-9])
                ot_payment = "{:>9,.2f}".format(response[8])
                ot_payment_rate = "{:>9,.2f}".format(response[9])
                hourly_payment_rate = "{:>9,.2f}".format(response[10])
                basic_salary = "{:>9,.2f}".format(response[11])
                net_salary = "{:>9,.2f}".format(response[12])
                total_worked_days = response[-12]
                over_night_days = response[-11]

            elif emp.emp_type == 1:
                attendance_record_list = response[0]
                total_worked_days = response[1]
                total_ot_hours = response[2]
                attendance_allowance = 0
                attendance_allowance_final = "{:>9,.2f}".format(response[7])
                other_allowance = 0
                br_payment = "{:>9,.2f}".format(response[6])
                fixed_basic_salary = "{:>9,.2f}".format(response[5])
                room_charge ="{:>9,.2f}".format(response[12])
                epf = "{:>9,.2f}".format(response[11])
                total_advance_amount = "{:>9,.2f}".format(response[8])
                total_allowance = "{:>9,.2f}".format(response[13])
                total_deduction = "{:>9,.2f}".format(response[9])
                ot_payment = "{:>9,.2f}".format(response[4])
                ot_payment_rate = response[3]
                hourly_payment_rate = 0
                basic_salary = 0
                net_salary = "{:>9,.2f}".format(response[15])
                total_working_hours = 0
                over_night_days = 0

            return JsonResponse({'attendance_list': attendance_record_list, 'total_working_hours': total_working_hours, 'total_ot_hours':total_ot_hours, 'basic_salary': basic_salary, 'ot_payment': ot_payment, 'hourly_payment_rate': hourly_payment_rate, 'ot_payment_rate': ot_payment_rate, 'net_salary': net_salary, 'total_advance_amount': total_advance_amount, 'epf': epf, 'total_allowance': total_allowance, 'room_charge':room_charge,"fixed_basic_salary":fixed_basic_salary,'br_payment':br_payment,'other_allowance':other_allowance,'attendance_allowance':attendance_allowance_final,'total_deduction':total_deduction,'total_worked_days':total_worked_days,'over_night_worked_days':over_night_days}, status=200)
        
