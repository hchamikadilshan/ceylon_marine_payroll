from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse,FileResponse
from payroll.views import get_final_salary_details
from employee.models import Employee

import io
from reportlab.lib.pagesizes import A4,landscape
from reportlab.platypus import SimpleDocTemplate,Table,TableStyle,Frame
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch,cm

# Create your views here.
class SalarySignatureReport(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def get(self,request):
        user = request.user
        return render(request,'salary_signature_report.html' ,context={'user':user})
    def post(self,request):
        emp_type = request.POST["emp_type"]
        month_year = request.POST["month_year"]
        month_year_split = month_year.split('-')
        response_employees = []
        if emp_type == 2:
            employees = Employee.objects.filter(active_status=True).values()
        else:
            employees = Employee.objects.filter(emp_type=emp_type,active_status=True).values()
        employees_list = list(employees)
        i = 0
        for employee in employees_list:
            try:
                employee_response = get_final_salary_details(emp_id=employee["emp_id"],month=month_year_split[1])
                if employee_response == "employee_finance_details_error":
                    pass
                else:
                    epf_no = employee_response[-3]
                    name = employee_response[-5]
                    department = employee_response[-4]
                    basic_salary = employee_response[3]
                    br_allowance = employee_response[2]
                    epf_12 = (basic_salary + br_allowance) * 0.12
                    epf_8 =(basic_salary + br_allowance) * 0.8
                    advance = employee_response[4] +employee_response[6]
                    ot = employee_response[8]
                    total_deduction = employee_response[5] + employee_response[6] + employee_response[4]
                    net_salary = employee_response[12]
                    response_employees.append([epf_no,name,department,f"{basic_salary:9.2f}",f"{br_allowance:9.2f}",f"{epf_12:9.2f}",f"{epf_8:9.2f}",f"{advance:9.2f}",f"{ot:9.2f}",f"{(total_deduction):9.2f}",f"{net_salary:9.2f}"])
            except (ValueError,IndexError):
                pass
        file_name = f"2023-03_Salary_Signature Sheet.pdf"
        title = f"2023-03 Salary Signature Sheet"
        buffer = io.BytesIO() 
        pdf = SimpleDocTemplate(buffer,pagesize = landscape(A4), title=title,showBoundary=1,leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0,)
        
        table_data = []
        document_heading = [f"2023-03 Salary Signature Sheet"]
        empty_row_heading =[""]
        table_data.append(document_heading)
        table_data.append(empty_row_heading)
#         table_heading = ['Emp ID', 'Name','Basic Salary',"""B R 
# Allowance""","""Other 
# Allowance""",'OT Payment',"""Total 
# Allowance""",'EPF',"""Total 
# Deductions""", 'Net Salary','Signature']
        table_heading = ["""Employee
No""", 'Name','Designation',"""Basic 
Salary""","""BR
Allowance""",'Total EPF',"""Deductions""",'EPF',"""Additions""", 'Net Salary',"Net Salary",'Signature']
        table_row_empty = ["","","","","","","EPF 8%","Advance","OT","Others"]
        
        table_data.append(table_heading)
        table_data.append(table_row_empty)
        for emp in response_employees:
            table_row = [emp[0], emp[1], emp[2],emp[3], emp[4], emp[5],emp[6], emp[7], emp[8],emp[9],emp[10], ""]
            table_data.append(table_row)
        elements = []
        # attendance_table = Table(table_data,colWidths=[0.6*inch,2.4*inch,0.8*inch,0.8*inch,0.8*inch,0.8*inch,0.8*inch,0.7*inch,0.7*inch,0.8*inch,2.0*inch],rowHeights=[0.3*inch for i in range(len(response_employees)+3)])
        attendance_table = Table(table_data,colWidths=[0.6*inch,1.9*inch,1.3*inch,0.8*inch,0.8*inch,0.75*inch,0.75*inch,0.7*inch,0.7*inch,0.8*inch,0.8*inch,1.5*inch],rowHeights=[0.3*inch for i in range(len(response_employees)+4)])
        attendance_table_styles = TableStyle(
    [
        ('GRID', (0, 2), (-1, -1), 1, colors.black),
        ('FONT', (0, 0), (0, 0), 'Helvetica-Bold',15),
        ('FONT', (0, 2), (-1, -1), 'Helvetica',9),
        # ('SPAN', (0, 0), (0, 0)),
        ('SPAN', (0, 0), (-1, 0)),
        ('SPAN', (0, 2), (0, 3)),
        ('SPAN', (1, 2), (1, 3)),
        ('SPAN', (2, 2), (2, 3)),
        ('SPAN', (3, 2), (3, 3)),
        ('SPAN', (4, 2), (4, 3)),
        ('SPAN', (5, 2), (5, 3)),
        ('SPAN', (10, 2), (10, 3)),
        ('SPAN', (11, 2), (11, 3)),
        ('SPAN', (6, 2), (7, 2)),
        ('SPAN', (8, 2), (9, 2)),
        ('ALIGN', (0, 0), (-1, 3),'CENTER'),
        ('ALIGN', (0, 0), (0,0),'CENTER'),
        ('ALIGN', (3, 4), (-1, -1),'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1),'MIDDLE'),
        ]
    
)
        attendance_table.setStyle(attendance_table_styles)
        elements.append(attendance_table)
        pdf.build(elements)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=file_name)
        
      