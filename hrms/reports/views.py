from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse,FileResponse
from payroll.views import get_process_salary,calculate_salary,get_final_salary_details
from employee.models import Employee,Bank,BankBranch
from adminapp.models import Company
from dashboard.models import MonthSummary
import locale
import io
from reportlab.lib.pagesizes import A4,landscape,legal
from reportlab.platypus import SimpleDocTemplate,Table,TableStyle,Frame,Paragraph,KeepTogether,PageBreak
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch,cm
import decimal
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from operator import itemgetter
from django.http import HttpResponse
from PyPDF2 import PdfReader, PdfWriter

def add_data_to_dashboard_model(year,month,total_salary,total_salary_advance,total_allowance,total_epf,employees_count):
    record =  MonthSummary.objects.filter(year=year,month=month)
    if record:
        monthly_record_obj = MonthSummary.objects.get(year=year,month=month)
        if(monthly_record_obj.total_salary != total_salary):
            monthly_record_obj.total_salary = total_salary
            monthly_record_obj.total_allowance = total_allowance
            monthly_record_obj.total_epf = total_epf
            monthly_record_obj.total_salary_advance = total_salary_advance
            monthly_record_obj.no_of_employees = employees_count
            monthly_record_obj.save()
    else:
        month_summary =  MonthSummary(month=month,year=year,total_salary=total_salary,total_salary_advance=total_salary_advance,total_allowance=total_allowance,total_epf=total_epf,no_of_employees=employees_count)
        month_summary.save()


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
            employees = Employee.objects.filter(active_status=True)
        else:
            employees = Employee.objects.filter(emp_type=emp_type,active_status=True)
        employees_list = list(employees)
        i = 0
        for employee in employees:
            try:
                employee_response = get_final_salary_details(employee,month=month_year_split[1],year=month_year_split[0])
                if employee_response == "employee_finance_details_error":
                    pass
                elif (employee.emp_type==0 and employee_response[-1]== 0) or (employee.emp_type==1 and employee_response[1]== 0):
                    pass
                else:
                    if employee.emp_type ==  0:
                        epf_no = employee_response[-3]
                        name = employee_response[-5]
                        department = employee_response[-4]
                        basic_salary = employee_response[3]
                        br_allowance = employee_response[2]
                    
                        epf_8 =employee_response[5]
                        if epf_8 == 0:
                            epf_12 = 0
                        else:
                            #  epf_12 = (basic_salary + br_allowance) * 0.12
                            epf_12 = employee_response[-8]
                        advance = employee_response[4] +employee_response[6]
                        ot = employee_response[8]
                        total_deduction = employee_response[5] + employee_response[6] + employee_response[4]
                        other = employee_response[7] + employee_response[16] + employee_response[18] + employee_response[1]
                        net_salary = employee_response[12]
                        response_employees.append([epf_no,name,department,f"{basic_salary:9.2f}",f"{br_allowance:9.2f}",f"{epf_12:9.2f}",f"{epf_8:9.2f}",f"{advance:9.2f}",f"{ot:9.2f}",f"{(other):9.2f}",f"{net_salary:9.2f}"])
                    elif employee.emp_type == 1:
                        epf_no =  employee.epf_no
                        name = employee.name
                        department = employee.dprtmnt.department
                        basic_salary = employee_response[5]
                        br_allowance = employee_response[6]
                        epf_12 =  (basic_salary + br_allowance) * 0.12
                        epf_8 = employee_response[11]
                        advance = employee_response[8]
                        ot = employee_response[4]
                        other = employee_response[13] + employee_response[7]
                        net_salary = employee_response[15]
                        response_employees.append([epf_no,name,department,f"{basic_salary:9,.2f}",f"{br_allowance:9,.2f}",f"{epf_12:9,.2f}",f"{epf_8:9,.2f}",f"{advance:9,.2f}",f"{ot:9,.2f}",f"{(other):9,.2f}",f"{net_salary:9,.2f}"])
            except (ValueError,IndexError):
                pass
        file_name = f"{month_year}_Salary_Signature Sheet.pdf"
        title = f"{month_year} Salary Signature Sheet"
        buffer = io.BytesIO() 
        pdf = SimpleDocTemplate(buffer,pagesize = landscape(A4), title=title,showBoundary=1,leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0,)
        
        table_data = []
        document_heading = [f"{month_year} Salary Signature Sheet"]
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
Allowance""",'EPF 12%',"""Deductions""",'EPF',"""Additions""", 'Net Salary',"Net Salary",'Signature']
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
    

class BankTranferReport(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def get(self,request):
        user = request.user
        banks = Bank.objects.all()
        return render(request,'bank_report.html' ,context={'user':user,'banks':banks})
    def post(self,request):
        year_month = request.POST["month"]
        year_month_split = year_month.split('-')
        # employees = Employee.objects.filter(emp_type=0,active_status=True).values()
        # employees_list = list(employees)
        payslips_record = []
        
        # employees_data = get_process_salary("multiple",year_month_split[1])
        employees =  Employee.objects.filter()
        employee_list =  list(employees)
        no = 0
        for employee in employees:
            try :
                net_salary = "{:>9,.2f}".format(0.0)
                response = get_final_salary_details(employee,month=year_month_split[1],year= year_month_split[0])
                # response = calculate_salary(employee[0],employee[1],employee[2],employee[3],employee[4],year_month_split[1])
                if employee.emp_type == 0:
                    net_salary = "{:>9,.2f}".format(response[12])
                elif employee.emp_type == 1:
                    net_salary = "{:>9,.2f}".format(response[15])
                    
                if response == "employee_finance_details_error":
                    payslips_record.append({"status":2})
                elif response == "Department Empty":
                    payslips_record.append({"status":3})
                elif (employee.emp_type == 0 and response[-1] == 0)  or (employee.emp_type == 1 and response[1] == 0):
                    print(f"{employee.emp_id} {employee.emp_type}")
                    pass
                elif (employee.bank == None or employee.branch == None or employee.bank_acc_no == "" or employee.bank_acc_name == "" ):
                    no += 1
                    payslips_record.append({'no':no,'emp_id':employee.emp_id if (employee.emp_id)[0]=="A" else f"A{(employee.emp_id[1::])}","name":employee.name,"month":year_month,'net_salary':net_salary,"status":4})
                else:
                    no += 1
                    payslips_record.append({'no':no,'emp_id':employee.emp_id if (employee.emp_id)[0]=="A" else f"A{(employee.emp_id[1::])}","name":employee.name,"month":year_month,'net_salary':net_salary,"status":0})
            except (ValueError,IndexError):
                payslips_record.append({'emp_id':employee.emp_id if (employee.emp_id)[0]=="A" else f"A{(employee.emp_id[1::])}","name":employee.name,"month":year_month,"status":1})
        return JsonResponse({"data":payslips_record})
    
class BankTranferReportPDF(LoginRequiredMixin,View):

    login_url = '/accounts/login'
    def post(self,request):
        year_month = request.POST["month_year"]
        year_month_split = year_month.split('-')
        month=year_month_split[1]
        year = year_month_split[0]
        emp_ids = request.POST["emp_ids"]
        emp_ids_list = emp_ids.split(',')
        employees = Employee.objects.filter(emp_id__in=emp_ids_list)
        employee_records = []
        total_salary = 0
        total_salary_advance = 0
        total_epf = 0
        total_allowance = 0
        employees_count = 0
        for employee in employees:
            emp_id = employee.emp_id
            try :
                response = get_final_salary_details(employee,month=month,year=year)
                if employee.emp_type == 0:
                    net_salary = "{:>9,.2f}".format(response[12])
                elif employee.emp_type == 1:
                    net_salary = "{:>9,.2f}".format(response[15])
                if response == "employee_finance_details_error":
                    pass
                elif response == "Department Empty":
                    pass
                elif response[-1] == 0:
                    pass
                elif (employee.bank == None or employee.branch == None or employee.bank_acc_no == "" or employee.bank_acc_name == "" ):
                    pass
                else:
                    if employee.emp_type == 0:    
                        total_salary += response[12]
                        total_salary_advance  += response[6]
                        total_epf += response[5]
                        total_allowance += response[7]
                        employees_count += 1
                    elif employee.emp_type == 1:
                        total_salary += response[15]
                        total_salary_advance  += response[8]
                        total_epf += response[11]
                        total_allowance += response[13]
                        employees_count += 1
                    employee_records.append([employee.emp_id if (employee.emp_id)[0]=="A" else f"A{(employee.emp_id[1::])}",employee.bank_acc_name,employee.bank_acc_no,employee.bank.bank_name,employee.branch.branch_name,net_salary])
            except (ValueError,IndexError):
                pass
        add_data_to_dashboard_model(year,month,total_salary,total_salary_advance,total_allowance,total_epf,employees_count)
        # employees = Employee.objects.filter(emp_type=0)
        # employees_list = list(employees)
        # employee_records = []
        # toatl_salary = 0
        # for employee in employees_list:
        #     emp_id = employee.emp_id
        #     try :
                
        #         response = get_final_salary_details(emp_id=emp_id,month=year_month_split[1])
        #         net_salary = "{:>9,.2f}".format(response[12])
        #         if response == "employee_finance_details_error":
        #             pass
        #         elif response == "Department Empty":
        #             pass
        #         elif response[-1] == 0:
        #             pass
        #         elif (employee.bank == None or employee.branch == None or employee.bank_acc_no == "" or employee.bank_acc_name == "" ):
        #             pass
        #         else:    
        #             toatl_salary += response[12]
        #             employee_records.append([employee.emp_id,employee.bank_acc_name,employee.bank_acc_no,employee.bank.bank_name,employee.branch.branch_name,net_salary])
        #     except (ValueError,IndexError):
        #         pass
        # employees_data = get_process_salary("multiple",year_month_split[1])
        # employee_records = []
        # for employee in employees_data:
        #     try :
                
        #         response = calculate_salary(employee[0],employee[1],employee[2],employee[3],employee[4],year_month_split[1])
        #         net_salary = "{:>9,.2f}".format(response[12])
        #         if response == "employee_finance_details_error":
        #             pass
        #         elif response == "Department Empty":
        #             pass
        #         elif response[-1] == 0:
        #             pass
        #         elif (employee[0].bank == None or employee[0].branch == None or employee[0].bank_acc_no == "" or employee[0].bank_acc_name == "" ):
        #             pass
        #         else:    

        #             employee_records.append([employee[0].emp_id,employee[0].bank_acc_name,employee[0].bank_acc_no,employee[0].bank.bank_name,employee[0].branch.branch_name,net_salary])
        #     except (ValueError,IndexError):
        #         pass
        total_salary_formated = "{:>9,.2f}".format(total_salary)
        sorted_employee_data = sorted(employee_records, key=itemgetter(3))
        company_bank_account = Company.objects.get(id=4)
        file_name = "Bank_Transfer_Request.pdf"
        buffer = io.BytesIO() 
        pdf = SimpleDocTemplate(buffer,pagesize = A4, title="SPECIMEN Bank Transfer List",showBoundary=0,leftMargin=0, rightMargin=0, topMargin=2.9*inch, bottomMargin=1.15*inch,)
        table_data = []

        header_style = ParagraphStyle(name='HeaderStyle', fontSize=14, leading=16)
        

        styles = getSampleStyleSheet()
        paragraph_style = styles["Normal"]
        document_heading_wraped=[""]
        table_data.append(document_heading_wraped)
        empty_row_heading =[""]
        # table_data.append(document_heading)
        table_data.append(empty_row_heading)
        table_heading = ["""No""", """EMP
ID""","""EMP 
NAME""","""ACCOUNT 
NO""","""BANK""",'BRANCH',"""NET 
SALARY"""]
        no = 1
        table_data.append(table_heading)
        for  employee_record in sorted_employee_data:
                table_data_row = ([str(no),  employee_record[0], employee_record[1], employee_record[2], employee_record[3], employee_record[4], employee_record[5]])
                new_table_row =[]
                for cell in table_data_row:
                    cell_content = Paragraph(cell, paragraph_style)
                    new_table_row.append(cell_content)
                table_data.append(new_table_row)
                no = no + 1
        sub_total_row = ["Total","","","","","",total_salary_formated]
        table_data.append(sub_total_row)
        


        elements = []
        
        attendance_table = Table(table_data,colWidths=[0.4*inch,0.7*inch,1*inch,1.5*inch,1.8*inch,1.3*inch,1*inch])
        attendance_table_styles = TableStyle(
            [
                ('GRID', (0, 2), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 2), (-1, 2),'CENTER'),
                ('VALIGN', (0, 2), (-1, 2),'MIDDLE'),
                ('FONT', (0, 2), (-1, 2), 'Helvetica-Bold',12),
                ('ALIGN', (6, 2), (6, -1),'RIGHT'),
                ('SPAN', (0,0), (0, 1)),
                ('SPAN', (0,-1), (5, -1)),
                ('ALIGN', (0, -11), (5, -1),'CENTER'),
                ]
            
        )
        
        attendance_table.setStyle(attendance_table_styles)

        def create_header(canvas, doc):
            header_text = f"I am writing to formally request the transfer of salary amounts for my employees to their respective accounts as specified below on (____/__/__). As the employer of ({company_bank_account.name}), I kindly ask you to transfer the total amount of (Rs.{total_salary_formated}) from my bank account ({company_bank_account.bank_account_no}) to the individual accounts of my employees "
            header = Paragraph(header_text, header_style)
            header.wrapOn(canvas, doc.width - 1*inch, doc.topMargin )
            header.drawOn(canvas, doc.leftMargin + 0.5*inch, doc.height + doc.topMargin - header.height - 0.7*inch)

            frame = Frame(0, 1.15*inch, pdf.width, pdf.height - 1.13*inch, id='normal')
            frame.addFromList([attendance_table], canvas)
        # table_with_wrapper = KeepTogether([attendance_table])

        elements.append(attendance_table)
        pdf.build(elements,onFirstPage=create_header, onLaterPages=create_header)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=file_name)

   
class EpfCForm(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def get(self,request):
        user = request.user
        return render(request,'epf_c_form.html' ,context={'user':user})
    def post(self,request):
        company = Company.objects.get(id=4)
        email = company.email
        contact_no = company.contact_no
        company_epf_no = company.epf_no
        bank_branch = company.bank_branch

        year_month = request.POST["month_year"]
        year_month_split = year_month.split('-')
        month = year_month_split[1]
        buffer = io.BytesIO()

        employees = Employee.objects.filter()
        employees_list = list(employees)
        employee_records = []
        for employee in employees:
            emp_id = employee.emp_id
            try :
                response = get_final_salary_details(employee,month=month,year=year_month_split[0])
                if response == "employee_finance_details_error":
                    pass
                elif response == "Department Empty":
                    pass
                elif (employee.emp_type ==0 and response[-1] == 0) or (employee.emp_type == 1 and response[1] == 0) :
                    pass
                elif employee.emp_type == 0 and response[-3]=="":
                    pass
                else:   
                    employee_records.append([employee,response])
            except (ValueError,IndexError):
                pass
        
        total_contribution = 0
        data_list = []
        for record in employee_records:
            if record[0].emp_type == 0:
                net_salary = "{:>9,.2f}".format(record[1][12])
                fixed_basic_salary = record[1][2] + record[1][3]
                total_earning = "{:>9,.2f}".format(fixed_basic_salary)
            elif record[0].emp_type == 1:
                fixed_basic_salary = record[1][5] + record[1][6]
                total_earning = "{:>9,.2f}".format(fixed_basic_salary)

            employees = fixed_basic_salary * 0.08
            employees_string = "{:>9,.2f}".format(fixed_basic_salary * 0.08)
            employees_int = int(fixed_basic_salary * 0.08)
            employees_float = employees_string[-2:]

            employers = fixed_basic_salary * 0.12
            employers_string = "{:>9,.2f}".format(employers)
            employers_int = int(employers)
            employers_float = employers_string[-2:]

            total_epf =  employers + employees
            total_epf_string = "{:>9,.2f}".format(total_epf)
            total_epf_int = int(total_epf)
            total_rpf_float = total_epf_string[-2:]
            total_contribution += total_epf    
            name = record[0].name
            epf_no = record[0].epf_no
            nic_no = record[0].nic_no
            data_list.append([name,nic_no,epf_no,total_epf_int,total_rpf_float,employers_int,employers_float,employees_int,employees_float,total_earning])

        # Employee Data Table Frame
        # employees_data = get_process_salary("multiple",month)
        # data_list = []
        # i=1
        # total_contribution = 0
        # for employee in employees_data:
        #     try:
        #         if employee[2]["epf_type"] == "1": # type: ignore
                    
        #             try :
        #                 response = calculate_salary(employee[0],employee[1],employee[2],employee[3],employee[4],year_month_split[1])
        #                 net_salary = "{:>9,.2f}".format(response[12])
        #                 if response == "employee_finance_details_error":
        #                     pass
        #                 elif response == "Department Empty":
        #                     pass
        #                 elif response[-1] == 0:
        #                     pass
        #                 else:
        #                     fixed_basic_salary = response[2] + response[3]
        #                     total_earning = "{:>9,.2f}".format(fixed_basic_salary)

        #                     employees = fixed_basic_salary * 0.08
        #                     employees_string = "{:>9.2f}".format(fixed_basic_salary * 0.08)
        #                     employees_int = int(fixed_basic_salary * 0.08)
        #                     employees_float = employees_string[-2:]

        #                     employers = fixed_basic_salary * 0.12
        #                     employers_string = "{:>9.2f}".format(employers)
        #                     employers_int = int(employers)
        #                     employers_float = employers_string[-2:]

        #                     total_epf =  employers + employees
        #                     total_epf_string = "{:>9.2f}".format(total_epf)
        #                     total_epf_int = int(total_epf)
        #                     total_rpf_float = total_epf_string[-2:]
        #                     # if response[11] > fixed_basic_salary:
        #                     #     total_earning = "{:>9,.2f}".format(fixed_basic_salary)

        #                     #     employees = fixed_basic_salary * 0.08
        #                     #     employees_string = "{:>9.2f}".format(fixed_basic_salary * 0.08)
        #                     #     employees_int = int(fixed_basic_salary * 0.08)
        #                     #     employees_float = employees_string[-2:]

        #                     #     employers = fixed_basic_salary * 0.12
        #                     #     employers_string = "{:>9.2f}".format(employers)
        #                     #     employers_int = int(employers)
        #                     #     employers_float = employers_string[-2:]

        #                     #     total_epf =  employers + employees
        #                     #     total_epf_string = "{:>9.2f}".format(total_epf)
        #                     #     total_epf_int = int(total_epf)
        #                     #     total_rpf_float = total_epf_string[-2:]
                                
        #                     # else:
        #                     #     total_earning = "{:>9,.2f}".format(response[11])

        #                     #     employees = response[11] * 0.08
        #                     #     employees_string = "{:>9.2f}".format(employees)
        #                     #     employees_int = int(response[11] * 0.08)
        #                     #     employees_float = employees_string[-2:]
                                
        #                     #     employers = response[11] * 0.12
        #                     #     employers_string = "{:>9.2f}".format(employers)
        #                     #     employers_int = int(employers)
        #                     #     employers_float = employers_string[-2:]

        #                     #     total_epf =  employers + employees
        #                     #     total_epf_string = "{:>9.2f}".format(total_epf)
        #                     #     total_epf_int = int(total_epf)
        #                     #     total_rpf_float = total_epf_string[-2:]
        #                     total_contribution += total_epf    
        #                     name = response[-5]
        #                     epf_no = response[-3]
        #                     nic_no = response[-7]
        #                     data_list.append([name,nic_no,epf_no,total_epf_int,total_rpf_float,employers_int,employers_float,employees_int,employees_float,total_earning])
        #                     i +=1
        #             except (ValueError,IndexError):
        #                 pass
        #     except TypeError:
        #         pass
        # Right Frame 
        no_of_pages = (len(data_list)//22) + 1

        if no_of_pages == 1:
            pdf = canvas.Canvas(buffer,pagesize = A4)

            flow_obj = []

            # Top Frame Table
            row1 = ["C","FORM EPF Act No of 1958"]

            table_data = []



            table_data.append(row1)

            table = Table(table_data,colWidths=[1.5*inch,3.5*inch,3*inch],rowHeights=[0.6*inch])
            table_styles = TableStyle(
                [
                    ('ALIGN', (0, 0), (0, 0),'RIGHT'),
                    ('FONT', (0, 0), (0, 0), 'Helvetica-Bold',22),
                    ('BOX', (0, 0), (-1, -1), 3, colors.black),
                    ('VALIGN', (0, 0), (-1, -1),'MIDDLE'),
                    ('FONT', (0, 0), (0, 0), 'Helvetica-Bold'),

                    ('FONT', (2, 1), (2, 1), 'Helvetica',13),
                    ('ALIGN', (2, 1), (2, 1),'CENTER'),
                    ('ALIGN', (1, 1), (1, 1),'CENTER'),
                    ('VALIGN', (0, 1), (-1, 1),'MIDDLE'),
                    ]
                
            )
            table.setStyle(table_styles)

            frame1 = Frame(0*inch,10.68*inch,8.3*inch,0.8*inch,showBoundary=0)


            flow_obj.append(table)
            frame1.addFromList(flow_obj,pdf)

            flow_obj = []
            table_data = []
            total_contribution = "{:>9,.2f}".format(total_contribution)
            row1 = ["EPF Registration No","",company_epf_no]
            row2 = ["Contribution for the Month of","",year_month]
            row3 = ["Contributions","",f"Rs {total_contribution}"]
            row4 = ["Surcharge","",""]
            row6 = ["Total Remittance","",f"Rs {total_contribution}"]
            row7 = ["Cheque No","",""]
            row8 = ["Bank & Branch","",bank_branch]

            table_data.append(row1)
            table_data.append(row2)
            table_data.append(row3)
            table_data.append(row4)
            table_data.append(row6)
            table_data.append(row7)
            table_data.append(row8)
            table = Table(table_data)
            table_styles = TableStyle(
                [
                    ('FONT', (0, 0), (-1, -1), 'Helvetica',9),
                    ('GRID', (0, 0), (-1,-1), 1, colors.black),
                    ('SPAN', (0, 2), (1, 2)),
                    ('SPAN', (0, 3), (1, 3)),
                    ('SPAN', (0, 4), (1, 4)),
                    ('SPAN', (0, 5), (1, 5)),
                    ('SPAN', (0, 6), (1, 6)),
                    ('SPAN', (0, 7), (1, 7)),
                    ('SPAN', (0, 0), (1, 0)),
                    ('SPAN', (0, 1), (1, 1)),
                    
                    ]
            )
            table.setStyle(table_styles)
            flow_obj.append(table)
            frame3 = Frame(0*inch,7.65*inch,8.3*inch,3*inch,showBoundary=0)
            frame3.addFromList(flow_obj,pdf)
            flow_obj = []
            table_data = []   
            row1 = ["Employee Name","NIC No","""Member 
        No""","Contibution","","","","","","""Total 
        Earnings"""]
            row2 = ["","","","Total","","Employer","","Employee","",""]   
            table_data.append(row1)
            table_data.append(row2)  
            for employee in data_list:
                row = [employee[0],employee[1],employee[2],employee[3],employee[4],employee[5],employee[6],employee[7],employee[8],employee[9]]
                table_data.append(row) 
                print(row)
            table = Table(table_data,colWidths=[2.7*inch,1.1*inch,0.7*inch,0.4*inch,0.3*inch,0.4*inch,0.3*inch,0.4*inch,0.3*inch,0.8*inch])
            table_styles = TableStyle(
                [
                    ('FONT', (0, 0), (-1, -1), 'Helvetica',9.1),
                    ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold',8),
                    ('GRID', (0, 0), (-1,-1), 1, colors.black),
                    ('SPAN', (0, 0), (0, 1)),
                    ('SPAN', (1, 0), (1, 1)),
                    ('SPAN', (2, 0), (2, 1)),
                    ('SPAN', (3, 1), (4, 1)),
                    ('SPAN', (5, 1), (6, 1)),
                    ('SPAN', (7, 1), (8, 1)),
                    ('SPAN', (3, 0), (8, 0)), #Contributon
                    ('SPAN', (9, 0), (9, 1)),
                    ('ALIGN', (0, 0), (-1, 0),'CENTER'),
                    ('VALIGN', (0, 0), (-1, 0),'MIDDLE'),
                    
                    ]
            )
            table.setStyle(table_styles)
            flow_obj.append(table)
            frame4 = Frame(0.08*inch,1.7*inch,8.1*inch,7.2*inch,showBoundary=0)
            frame4.addFromList(flow_obj,pdf)

            # Footer Part
            flow_obj = []
            table_data = []

            row1 = ["""Please write Employer's E.P.F Registration Number on the reverse if the cheque""","",""]
            row2 = ["I certify that information given above is correct","","","","",""]
            row3 = [f"Telephone No:{contact_no}",f"E-mail Address {email}","","","",""]
            rowEmpty = ["","","","","",""]
            row4 = ["                                      ..........................................................","                                 ..........................","","","",""]
            row5 = ["                                           Signature of the Employer","                                          Date","","","",""]

            table_data.append(row1)
            table_data.append(row2)
            table_data.append(row3)
            table_data.append(rowEmpty)
            table_data.append(row4)
            table_data.append(row5)
            table = Table(table_data,colWidths=[4*inch,4.0*inch,0*inch,0*inch,0*inch,0*inch])
            table_styles = TableStyle(
                [
                    ('FONT', (0, 0), (-1, -1), 'Helvetica',9),
                    # ('GRID', (0, 0), (-1,-1), 1, colors.black),
                    # ('SPAN', (1, 0), (2, 0)),
                    ]
            )
            table.setStyle(table_styles)
            flow_obj.append(table)
            frame5 = Frame(0.08*inch,0.08*inch,8.1*inch,1.6*inch,showBoundary=0)
            frame5.addFromList(flow_obj,pdf)
            pdf.setTitle(f"{year_month}-EPF C FORM")
            pdf.save()
        else:
            title = f"{year_month} EPF C Form"
            pdf = SimpleDocTemplate(buffer,pagesize =A4, title=title,showBoundary=1,leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0,)
            flow_obj = []

            # Top Frame Table
            row1 = ["C","FORM EPF Act No of 1958"]



            table_data = []

            table_data.append(row1)

            table = Table(table_data,colWidths=[1.5*inch,3.5*inch,3*inch],rowHeights=[0.6*inch])
            table_styles = TableStyle(
                [
                    ('ALIGN', (0, 0), (0, 0),'RIGHT'),
                    ('FONT', (0, 0), (0, 0), 'Helvetica-Bold',22),
                    ('BOX', (0, 0), (-1, -1), 3, colors.black),
                    ('VALIGN', (0, 0), (-1, -1),'MIDDLE'),
                    ('FONT', (0, 0), (0, 0), 'Helvetica-Bold'),

                    ('FONT', (2, 1), (2, 1), 'Helvetica',13),
                    ('ALIGN', (2, 1), (2, 1),'CENTER'),
                    ('ALIGN', (1, 1), (1, 1),'CENTER'),
                    ('VALIGN', (0, 1), (-1, 1),'MIDDLE'),
                    ]
                
            )
            table.setStyle(table_styles)
            flow_obj.append(table)

            

            table_data = []
            total_contribution = "{:>9,.2f}".format(total_contribution)
            empty_row = [""]
            row1 = ["EPF Registration No","",company_epf_no]
            row2 = ["Contribution for the Month of","",year_month]
            row3 = ["Contributions","",f"Rs {total_contribution}"]
            row4 = ["Surcharge","",""]
            row6 = ["Total Remittance","",f"Rs {total_contribution}"]
            row7 = ["Cheque No","",""]
            row8 = ["Bank & Branch","",bank_branch]
            empty_row = [""]

            table_data.append(empty_row)
            table_data.append(row1)
            table_data.append(row2)
            table_data.append(row3)
            table_data.append(row4)
            table_data.append(row6)
            table_data.append(row7)
            table_data.append(row8)
            table_data.append(empty_row)
            table = Table(table_data)
            table_styles = TableStyle(
                [
                    ('FONT', (0, 0), (-1, -1), 'Helvetica',9),
                    ('GRID', (0, 1), (-1,-2), 1, colors.black),
                    ('SPAN', (0, 2), (1, 2)),
                    ('SPAN', (0, 3), (1, 3)),
                    ('SPAN', (0, 4), (1, 4)),
                    ('SPAN', (0, 5), (1, 5)),
                    ('SPAN', (0, 6), (1, 6)),
                    ('SPAN', (0, 7), (1, 7)),
                    ('SPAN', (0, 0), (1, 0)),
                    ('SPAN', (0, 1), (1, 1)),
                    
                    ]
            )
            table.setStyle(table_styles)
            flow_obj.append(table)

            table_data= []

            data_table_row1 = ["Employee Name","NIC No","""Member 
No""","Contibution","","","","","","""Total 
Earnings"""]
            data_table_row2 = ["","","","Total","","Employer","","Employee","",""]   
            table_data.append(data_table_row1)
            table_data.append(data_table_row2) 

            for employee in data_list:
                row = [employee[0],employee[1],employee[2],employee[3],employee[4],employee[5],employee[6],employee[7],employee[8],employee[9]]
                table_data.append(row)  
            empty_row = [""]
            table_data.append(empty_row)

            table = Table(table_data,colWidths=[2.7*inch,1.1*inch,0.7*inch,0.4*inch,0.3*inch,0.4*inch,0.3*inch,0.4*inch,0.3*inch,0.8*inch])
            table_styles = TableStyle(
                [
                    ('GRID', (0, 0), (-1,-2), 1, colors.black), # data table

                    ('SPAN', (0, 0), (-1, 0)),
                    ('ALIGN', (0, 0), (-1, 0),'CENTER'),

                    ('SPAN', (0, 0), (0, 1)), #Employee No
                    ('SPAN', (1, 0), (1, 1)), #NIC No
                    ('SPAN', (2, 0), (2, 1)), #Member No
                    ('SPAN', (3, 1), (4, 1)), 
                    ('SPAN', (5, 1), (6, 1)), #Member No
                    ('SPAN', (7, 1), (8, 1)), #Member No
                    ('ALIGN', (2, 2), (2, -1),'CENTER'),#Member No
                    ('ALIGN', (3, 2), (3, -1),'CENTER'), # Contibution Total
                    ('ALIGN', (5, 2), (5, -1),'CENTER'), # Employer Total
                    ('ALIGN', (7, 2), (7, -1),'CENTER'), # Employee Total
                    ('SPAN', (3, 0), (8, 0)), #Contributon
                    ('SPAN', (9, 0), (9, 1)), #Total Earning
                    ]
                
            )
            table.setStyle(table_styles)
            flow_obj.append(table)

            table_data = []

            row1 = ["""Please write Employer's E.P.F Registration Number on the reverse if the cheque""","",""]
            row2 = ["I certify that information given above is correct","","","","",""]
            row3 = [f"Telephone No:{contact_no}",f"E-mail Address {email}","","","",""]
            rowEmpty = ["","","","","",""]
            row4 = ["                                      ..........................................................","                                 ..........................","","","",""]
            row5 = ["                                           Signature of the Employer","                                          Date","","","",""]

            table_data.append(row1)
            table_data.append(row2)
            table_data.append(row3)
            table_data.append(rowEmpty)
            table_data.append(row4)
            table_data.append(row5)
            table = Table(table_data,colWidths=[4*inch,4.0*inch,0*inch,0*inch,0*inch,0*inch])
            table_styles = TableStyle(
                [
                    ('FONT', (0, 0), (-1, -1), 'Helvetica',9),
                    # ('GRID', (0, 0), (-1,-1), 1, colors.black),
                    # ('SPAN', (1, 0), (2, 0)),
                    ]
            )
            table.setStyle(table_styles)
            flow_obj.append(table)
            pdf.build(flow_obj)

            

        
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f"{year_month}-epf-C-Form.pdf")
 
        
class EtfReport(LoginRequiredMixin,View):

    def get(self,request):
        return render(request,"etf_report.html")
    def post(self,request):
        year = request.POST["year"]
        year_quater = request.POST["year_quarter"]
        month1_cheque_no = request.POST["month1_cheque_no"]
        month2_cheque_no = request.POST["month2_cheque_no"]
        month3_cheque_no = request.POST["month3_cheque_no"]
        month4_cheque_no = request.POST["month4_cheque_no"]
        month5_cheque_no = request.POST["month5_cheque_no"]
        month6_cheque_no = request.POST["month6_cheque_no"]
        month1_payment_date = request.POST["month1_payment_date"]
        month2_payment_date = request.POST["month2_payment_date"]
        month3_payment_date = request.POST["month3_payment_date"]
        month4_payment_date = request.POST["month4_payment_date"]
        month5_payment_date = request.POST["month5_payment_date"]
        month6_payment_date = request.POST["month6_payment_date"]
        if year_quater == "0":
            months = ["01","02","03","04","05","06"]
        else :
            months = ["07","08","09","10","11","12"]
        employees = Employee.objects.filter(emp_type=0)
        employees_list = list(employees)
        employee_records = []
        for month in months:
            for employee in employees:
                emp_id = employee.emp_id
                try :
                    response = get_final_salary_details(employee,month=month)
                    if response == "employee_finance_details_error":
                        employee_records.append([employee.name,employee.epf_no,employee.nic_no,month,0.0,"no_record"])
                    elif response == "Department Empty":
                        employee_records.append([employee.name,employee.epf_no,employee.nic_no,month,0.0,"no_record"])
                    elif response[-1] == 0:
                        employee_records.append([employee.name,employee.epf_no,employee.nic_no,month,0.0,"no_record"])
                    elif response[-3]=="":
                        employee_records.append([employee.name,employee.epf_no,employee.nic_no,month,0.0,"no_record"])
                    elif response[-11] == None or response[-11] == "2":
                        employee_records.append([employee.name,employee.epf_no,employee.nic_no,month,0.0,"no_record"])
                    else:  
                        response.append(month) 
                        employee_records.append(response)
                except (ValueError,IndexError,AttributeError):
                    employee_records.append([employee.name,employee.epf_no,employee.nic_no,month,0.0,"no_record"])
        data_list = {}
        total_contribution = 0
        for response in employee_records:
            if response[-1] == "no_record":
                epf_no = response[1]
                name = response[0]
                nic_no = response[2]
                etf = 0.0
                total_earning = 0.0
                month = response[-3]
                if epf_no in data_list:
        
                    new_records = []
                    records = data_list[epf_no]
                    for record in records:
                        new_records.append(record)
                    new_records.append([name,nic_no,epf_no,etf,month,total_earning])
                    data_list[epf_no] = new_records
                    
                else:
                    data_list[epf_no] = [[name,nic_no,epf_no,etf,month,total_earning]]
            else:
                net_salary = "{:>9,.2f}".format(response[12])
                fixed_basic_salary = response[2] + response[3]
                total_earning = "{:>9,.2f}".format(fixed_basic_salary)

                etf = fixed_basic_salary * 0.03
                etf_string = "{:>9.2f}".format(fixed_basic_salary * 0.03)
                etf_int = int(fixed_basic_salary * 0.08)
                etf_float = etf_string[-2:]

                name = response[-6]
                epf_no = response[-4]
                nic_no = response[-8]

                if epf_no in data_list:
                    new_records = []
                    records = data_list[epf_no]
                    for record in records:
                        new_records.append(record)
                    new_records.append([name,nic_no,epf_no,etf,response[-1],fixed_basic_salary])
                    data_list[epf_no] = new_records

                    
                else:
                    data_list[epf_no] = [[name,nic_no,epf_no,etf,response[-1],fixed_basic_salary]]
        
        data  = []
        all_total_contribution = 0
        month1_earning_total = 0
        month1_contribution_total = 0
        month2_earning_total = 0
        month2_contribution_total = 0
        month3_earning_total = 0
        month3_contribution_total = 0
        month4_earning_total = 0
        month4_contribution_total = 0
        month5_earning_total = 0
        month5_contribution_total = 0
        month6_earning_total = 0
        month6_contribution_total = 0
        for emp in data_list:
            name = data_list[emp][0][0]
            epf_no =  data_list[emp][0][2]
            nic_no = data_list[emp][0][1]
            total_contribution = data_list[emp][0][3] + data_list[emp][1][3] + data_list[emp][2][3]+ data_list[emp][3][3] + data_list[emp][5][3] 
            all_total_contribution += total_contribution
            all_total_contribution_formated = "{:>9,.2f}".format(all_total_contribution)
            total_contribution_formated = "{:>9,.2f}".format(total_contribution)

            month1_earning = data_list[emp][0][5]
            month1_earning_formated = "{:>9,.2f}".format(month1_earning)
            month1_contribution = data_list[emp][0][3]
            month1_contribution_formated = "{:>9,.2f}".format(month1_contribution)
            month1_earning_total += month1_earning
            month1_contribution_total += month1_contribution
            month1_contribution_total_formatted = "{:>9,.2f}".format(month1_contribution_total)
            month1_earning_total_formatted = "{:>9,.2f}".format(month1_earning_total)

            month2_earning = data_list[emp][1][5]
            month2_earning_formated = "{:>9,.2f}".format(month2_earning)
            month2_contribution = data_list[emp][1][3]
            month2_contribution_formated = "{:>9,.2f}".format(month2_contribution)
            month2_earning_total += month2_earning
            month2_contribution_total += month2_contribution
            month2_contribution_total_formatted = "{:>9,.2f}".format(month2_contribution_total)
            month2_earning_total_formatted = "{:>9,.2f}".format(month2_earning_total)

            month3_earning = data_list[emp][2][5]
            month3_earning_formated = "{:>9,.2f}".format(month3_earning)
            month3_contribution = data_list[emp][2][3]
            month3_contribution_formated = "{:>9,.2f}".format(month3_contribution)
            month3_earning_total += month3_earning
            month3_contribution_total += month3_contribution
            month3_contribution_total_formatted = "{:>9,.2f}".format(month3_contribution_total)
            month3_earning_total_formatted = "{:>9,.2f}".format(month3_earning_total)

            month4_earning = data_list[emp][3][5]
            month4_earning_formated = "{:>9,.2f}".format(month4_earning)
            month4_contribution = data_list[emp][3][3]
            month4_contribution_formated = "{:>9,.2f}".format(month4_contribution)
            month4_earning_total += month4_earning
            month4_contribution_total += month4_contribution
            month4_contribution_total_formatted = "{:>9,.2f}".format(month4_contribution_total)
            month4_earning_total_formatted = "{:>9,.2f}".format(month4_earning_total)

            month5_earning = data_list[emp][4][5]
            month5_earning_formated = "{:>9,.2f}".format(month5_earning)
            month5_contribution = data_list[emp][4][3]
            month5_contribution_formated = "{:>9,.2f}".format(month5_contribution)
            month5_earning_total += month5_earning
            month5_contribution_total += month5_contribution
            month5_contribution_total_formatted = "{:>9,.2f}".format(month5_contribution_total)
            month5_earning_total_formatted = "{:>9,.2f}".format(month5_earning_total)

            month6_earning = data_list[emp][5][5]
            month6_earning_formated = "{:>9,.2f}".format(month6_earning)
            month6_contribution = data_list[emp][5][3]
            month6_contribution_formated = "{:>9,.2f}".format(month6_contribution)
            month6_earning_total += month6_earning
            month6_contribution_total += month6_contribution
            month6_contribution_total_formatted = "{:>9,.2f}".format(month6_contribution_total)
            month6_earning_total_formatted = "{:>9,.2f}".format(month6_earning_total)
            if total_contribution == 0 or epf_no == "":
                pass
            else:
                data.append([name,epf_no,nic_no,total_contribution_formated,month1_earning_formated,month1_contribution_formated,month2_earning_formated,month2_contribution_formated,month3_earning_formated,month3_contribution_formated,month4_earning_formated,month4_contribution_formated,month5_earning_formated,month5_contribution_formated,month6_earning_formated,month6_contribution_formated])

        no_of_employees = len(data)
        title="ETF EMPLOYEE SUMMARY REPORT"
        buffer = io.BytesIO() 
        buffer2 = io.BytesIO() 
        elements = []
        pdf = SimpleDocTemplate(buffer,pagesize = landscape(legal), title=title,showBoundary=1,leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0,)
        cell_style = ParagraphStyle(name='my_cell_style', wordWrap='WORDWRAP')
        document_heading = [f"EMPLOYEE TRUST FUND BOARD"]
        empty_row_heading =[""]
        table_row_heading2 = ["FORM 11 RETURN","Return for period January to June 2023","","","","","","","","","","","",f"Total No of Employees:{no_of_employees}"]
        table_heading1 = ["""NAME
OF 
MEMBER""", """MEMBER
NUMBER""",'NIC',"""TOTAL 
CONTRI
BUTIONS""","""TOTAL GROSS WAGES AND CONTRIBUTION""","","","","","","","","","","",""]
        table_heading2 = ["","","","","JAN","","FEB","","MARCH","","APRIL","","MAY","","JUNE",""]
        table_row_empty = ["","","","","""TOTAL
EARNINGS""","""CONTRI
BUTIONS""","""TOTAL
EARNINGS""","""CONTRI
BUTIONS""","""TOTAL
EARNINGS""","""CONTRI
BUTIONS""","""TOTAL
EARNINGS""","""CONTRI
BUTIONS""","""TOTAL
EARNINGS""","""CONTRI
BUTIONS""","""TOTAL
EARNINGS""","""CONTRI
BUTIONS"""]

        table_total_row = ["Total","99,000.00","999,000.00",all_total_contribution_formated,month1_earning_total_formatted,month1_contribution_total_formatted,month2_earning_total_formatted,month2_contribution_total_formatted,month3_earning_total_formatted,month3_contribution_total_formatted,month4_earning_total_formatted,month4_contribution_total_formatted,month5_earning_total_formatted,month5_contribution_total_formatted,month6_earning_total_formatted,month6_contribution_total_formatted]
        table_bottom_row1 = ["EMPLOYER REGISTRATION NO","","A/56108","I certify that all the particulars given above are correct and that no part of the contributions that should be paid by us has been deducted from any emploees's earnings"]
        table_bottom_row2 = ["COMPANY NAME","","CEYLON MARINE SERVICES HOLDINGS PVT LTD",""]
        table_bottom_row3 = ["ADDRESS","","No.72, St. Andrews Road, Modera, Colombo 15","","","","_________________________","","","____________________________________________________"]
        table_bottom_row4 = ["TELEPHONE","","0772594469","","","","Date","","","Signature of the Employer"]
        table_bottom_empty_row = [""]

        no_of_pages = (len(data)//22) + 1
        print(len(data),no_of_pages)
        

        if no_of_pages == 1:
            table_data = []
            print("inside")
            table_data.append(document_heading)
            table_data.append(empty_row_heading)
            table_data.append(table_row_heading2)
            table_data.append(table_heading1)
            table_data.append(table_heading2)
            table_data.append(table_row_empty)
            for table_row in data:
                table_data.append(table_row)

            table_data.append(table_total_row)
            table_data.append(table_bottom_empty_row)
            table_data.append(table_bottom_row1)
            table_data.append(table_bottom_row2)
            table_data.append(table_bottom_row3)
            table_data.append(table_bottom_row4)
            attendance_table = Table(table_data,colWidths=[1.8*inch,0.7*inch,0.9*inch,0.7*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch])
            attendance_table_styles = TableStyle(
                [
                    ('GRID', (0, 3), (-1, -6), 1, colors.black),
                    ('GRID', (4,-6), (-1, -6), 1, colors.black), # Total
                    ('GRID', (2,-4), (2, -4), 1, colors.black), # Employer No
                    ('FONT', (0, 0), (0, 0), 'Helvetica-Bold',15),
                    ('FONT', (0, 2), (-1, 2), 'Helvetica-Bold',11),
                    ('FONT', (2, 4), (2, 7), 'Helvetica',10),
                    ('FONT', (0, 3), (-1, -1), 'Helvetica',9),
                    ('SPAN', (1, 2), (11, 2)), # Horozontal Span "Return for period January to June 2023"
                    ('SPAN', (0, 0), (-1, 0)), # Horozontal Span "Heading"
                    ('SPAN', (4, 3), (-1, 3)), # Horozontal Span "Total Gross Wages colum 1st row"
                    ('SPAN', (4, 4), (5, 4)), # Horozontal Span "July"
                    ('SPAN', (6, 4), (7, 4)), # Horozontal Span "AUG"
                    ('SPAN', (8, 4), (9, 4)), # Horozontal Span "SEP"
                    ('SPAN', (10, 4), (11, 4)), # Horozontal Span "OCT"
                    ('SPAN', (12, 4), (13, 4)), # Horozontal Span "NOV"
                    ('SPAN', (14, 4), (15, 4)), # Horozontal Span "DEC"
                    ('SPAN', (0, -6), (2, -6)), # Horozontal Span "Total"
                    ('SPAN', (0, -3), (1, -3)), # Horozontal Span "NAME TITLE"
                    ('SPAN', (0, -2), (1, -2)), # Horozontal Span "ADDRESS TITLE"
                    ('SPAN', (2, -2), (3, -2)), # ADDRESS"
                    ('SPAN', (2, -3), (3, -3)), # TITILE"
                    ('SPAN', (6, -2), (8, -2)), # Date ....... "
                    ('SPAN', (6, -1), (8, -1)), # Date"
                    ('SPAN', (9, -2), (-1, -2)), # Signature ....... "
                    ('SPAN', (9, -1), (-1, -1)), # Signature"
                    ('SPAN', (0, 3), (0, 5)),
                    ('SPAN', (1, 3), (1, 5)),
                    ('SPAN', (2, 3), (2, 5)),
                    ('SPAN', (3, 3), (3, 5)),
                    ('ALIGN', (0, -5), (3, -5),'RIGHT'), # Total
                    ('ALIGN', (0, 0), (-1, 3),'CENTER'),
                    ('ALIGN', (0, 5), (-1,5),'CENTER'),
                    ('ALIGN', (2, 3), (2, -1),'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1),'MIDDLE'),
                    ('ALIGN', (2, -3), (-1, -3),'LEFT'), # Telephone
                    ('ALIGN', (2, -2), (-1, -2),'LEFT'), # Address
                    ('ALIGN', (2, -1), (-1, -1),'LEFT'), # TELEPHONE
                    ('ALIGN', (6, -2), (8, -2),'CENTER'), # DATE ......
                    ('ALIGN', (6, -1), (8, -1),'CENTER'), # DATE
                    ('ALIGN', (9, -2), (-1, -2),'CENTER'), # DATE ......
                    ('ALIGN', (9, -1), (-1, -1),'CENTER'), # DATE
                    ]
                
            )
            attendance_table.setStyle(attendance_table_styles)
            elements.append(attendance_table)
        else:
            start = 0
            for page in range(no_of_pages):
                table_data = []
                end = start + 28
                table_data.append(document_heading)
                table_data.append(empty_row_heading)
                table_data.append(table_row_heading2)
                table_data.append(table_heading1)
                table_data.append(table_heading2)
                table_data.append(table_row_empty)
                if page != (range(no_of_pages)[-1]):
                    print(start,end)
                    for table_row in data[start:end]:
                        table_data.append(table_row)
                    attendance_table = Table(table_data,colWidths=[1.8*inch,0.7*inch,0.9*inch,0.7*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch])
                    attendance_table_styles = TableStyle(
                    [
                        ('GRID', (0, 3), (-1, -1), 1, colors.black),
                        ('GRID', (4,-6), (-1, -6), 1, colors.black), # Total
                        ('GRID', (2,-4), (2, -4), 1, colors.black), # Employer No
                        ('FONT', (0, 0), (0, 0), 'Helvetica-Bold',15),
                        ('FONT', (0, 2), (-1, 2), 'Helvetica-Bold',11),
                        ('FONT', (0, 3), (-1, -1), 'Helvetica',9),
                        ('FONT', (2, 4), (2, -1), 'Helvetica',8),
                        ('SPAN', (1, 2), (11, 2)), # Horozontal Span "Return for period January to June 2023"
                        ('SPAN', (0, 0), (-1, 0)), # Horozontal Span "Heading"
                        ('SPAN', (4, 3), (-1, 3)), # Horozontal Span "Total Gross Wages colum 1st row"
                        ('SPAN', (4, 4), (5, 4)), # Horozontal Span "July"
                        ('SPAN', (6, 4), (7, 4)), # Horozontal Span "AUG"
                        ('SPAN', (8, 4), (9, 4)), # Horozontal Span "SEP"
                        ('SPAN', (10, 4), (11, 4)), # Horozontal Span "OCT"
                        ('SPAN', (12, 4), (13, 4)), # Horozontal Span "NOV"
                        ('SPAN', (14, 4), (15, 4)), # Horozontal Span "DEC"
                        ('SPAN', (0, 3), (0, 5)),
                        ('SPAN', (1, 3), (1, 5)),
                        ('SPAN', (2, 3), (2, 5)),
                        ('SPAN', (3, 3), (3, 5)),
                        ('ALIGN', (0, 0), (-1, 3),'CENTER'),
                        ('ALIGN', (0, 5), (-1,5),'CENTER'),
                        ('ALIGN', (2, 3), (2, -1),'RIGHT'),
                        ('VALIGN', (0, 0), (-1, -1),'MIDDLE'),
                    ]
                
                    )
                    attendance_table.setStyle(attendance_table_styles)
                else:
                    print("last_page ",start,end)
                    table_data = []
                    table_data.append(document_heading)
                    table_data.append(empty_row_heading)
                    table_data.append(table_row_heading2)
                    table_data.append(table_heading1)
                    table_data.append(table_heading2)
                    table_data.append(table_row_empty)
                    for table_row in data[start:end]:
                        table_data.append(table_row)
                    table_data.append(table_total_row)
                    table_data.append(table_bottom_empty_row)
                    table_data.append(table_bottom_row1)
                    table_data.append(table_bottom_row2)
                    table_data.append(table_bottom_row3)
                    table_data.append(table_bottom_row4)
                    attendance_table = Table(table_data,colWidths=[1.8*inch,0.7*inch,0.9*inch,0.7*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch,0.75*inch])
                    attendance_table_styles = TableStyle(
                    [
                        ('GRID', (0, 3), (-1, -6), 1, colors.black),
                    ('GRID', (4,-6), (-1, -6), 1, colors.black), # Total
                    ('GRID', (2,-4), (2, -4), 1, colors.black), # Employer No
                    ('FONT', (0, 0), (0, 0), 'Helvetica-Bold',15),
                    ('FONT', (0, 2), (-1, 2), 'Helvetica-Bold',11),
                    ('FONT', (0, 3), (-1, -1), 'Helvetica',9),
                    ('FONT', (2, 4), (2, -7), 'Helvetica',8),
                    ('SPAN', (1, 2), (11, 2)), # Horozontal Span "Return for period January to June 2023"
                    ('SPAN', (0, 0), (-1, 0)), # Horozontal Span "Heading"
                    ('SPAN', (4, 3), (-1, 3)), # Horozontal Span "Total Gross Wages colum 1st row"
                    ('SPAN', (4, 4), (5, 4)), # Horozontal Span "July"
                    ('SPAN', (6, 4), (7, 4)), # Horozontal Span "AUG"
                    ('SPAN', (8, 4), (9, 4)), # Horozontal Span "SEP"
                    ('SPAN', (10, 4), (11, 4)), # Horozontal Span "OCT"
                    ('SPAN', (12, 4), (13, 4)), # Horozontal Span "NOV"
                    ('SPAN', (14, 4), (15, 4)), # Horozontal Span "DEC"
                    ('SPAN', (0, -6), (2, -6)), # Horozontal Span "Total"
                    ('SPAN', (0, -3), (1, -3)), # Horozontal Span "NAME TITLE"
                    ('SPAN', (0, -2), (1, -2)), # Horozontal Span "ADDRESS TITLE"
                    ('SPAN', (2, -2), (3, -2)), # ADDRESS"
                    ('SPAN', (2, -3), (3, -3)), # TITILE"
                    ('SPAN', (6, -2), (8, -2)), # Date ....... "
                    ('SPAN', (6, -1), (8, -1)), # Date"
                    ('SPAN', (9, -2), (-1, -2)), # Signature ....... "
                    ('SPAN', (9, -1), (-1, -1)), # Signature"
                    ('SPAN', (0, 3), (0, 5)),
                    ('SPAN', (1, 3), (1, 5)),
                    ('SPAN', (2, 3), (2, 5)),
                    ('SPAN', (3, 3), (3, 5)),
                    ('ALIGN', (0, -5), (3, -5),'RIGHT'), # Total
                    ('ALIGN', (0, 0), (-1, 3),'CENTER'),
                    ('ALIGN', (0, 5), (-1,5),'CENTER'),
                    ('ALIGN', (2, 3), (2, -1),'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1),'MIDDLE'),
                    ('ALIGN', (2, -3), (-1, -3),'LEFT'), # Telephone
                    ('ALIGN', (2, -2), (-1, -2),'LEFT'), # Address
                    ('ALIGN', (2, -1), (-1, -1),'LEFT'), # TELEPHONE
                    ('ALIGN', (6, -2), (8, -2),'CENTER'), # DATE ......
                    ('ALIGN', (6, -1), (8, -1),'CENTER'), # DATE
                    ('ALIGN', (9, -2), (-1, -2),'CENTER'), # DATE ......
                    ('ALIGN', (9, -1), (-1, -1),'CENTER'), # DATE
                    ]
                
                    )
                    attendance_table.setStyle(attendance_table_styles)
                start = end 
                elements.append(attendance_table)
                elements.append(PageBreak())





        attendance_table.setStyle(TableStyle([('STYLE', (0,0), (-1,-1), 'my_cell_style')]))

        pdf.build(elements)
        buffer.seek(0)


        pdf2 = SimpleDocTemplate(buffer2,pagesize = landscape(A4), title="2023-03_Salary_Signature Sheet",showBoundary=1,leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0,)
        table_data2 = []
        cell_style2 = ParagraphStyle(name='my_cell_style', wordWrap='WORDWRAP')
        document_heading1 = [f"EMPLOYEE TRUST FUND BOARD"]
        document_heading2 =["RETURN OF THE HALF - YEAR BEGINNING 31st June 2023"]
        document_heading3 =["CONTRIBUTOR'S RECONCILATION STATEMENT"]
        document_sub_heading1 =["1. DETAILS OF PAYMENTS"]
        table_data2.append(document_heading)
        table_data2.append(document_heading2)
        table_data2.append(document_heading3)
        table_data2.append(document_sub_heading1)
        table_heading1 = ["""Month""", """Total Monthly 
Contributions 
Payable as per 
Form II Return""","""Amount 
Remitted 
Monthly""","""Over/Under""","""Cheque No""","""Cheque 
Amont""","""Name & Branch 
of Bank Where 
Payment was 
made (If paid by 
cash)""","""Date of Payment"""]
        table_data2.append(table_heading1)
        # for emp in response_employees:
        #     table_row = [emp[0], emp[1], emp[2],'']
        #     table_data.append(table_row)

        data = [["Jan",month1_contribution_total_formatted,month1_contribution_total_formatted,"",month1_cheque_no,month1_contribution_total_formatted,"",month1_payment_date],
                ["Feb",month2_contribution_total_formatted,month2_contribution_total_formatted,"",month2_cheque_no,month2_contribution_total_formatted,"",month2_payment_date],
                ["March",month3_contribution_total_formatted,month3_contribution_total_formatted,"",month3_cheque_no,month3_contribution_total_formatted,"",month3_payment_date],
                ["April",month4_contribution_total_formatted,month4_contribution_total_formatted,"",month4_cheque_no,month4_contribution_total_formatted,"",month4_payment_date],
                ["May",month5_contribution_total_formatted,month5_contribution_total_formatted,"",month5_cheque_no,month5_contribution_total_formatted,"",month5_payment_date],
                ["June",month6_contribution_total_formatted,month6_contribution_total_formatted,"",month6_cheque_no,month6_contribution_total_formatted,"",month6_payment_date],
                ["Total",all_total_contribution_formated,all_total_contribution_formated,"","",""],
                ]
        for table_row in data:
            table_data2.append(table_row)
        # table_row = ["A.B.C.D.E. Hapuarachchi","200","200113902674","3500.00","15,000.00"]
        table_total_row = ["2.SUMMARY OF RETURN"]
        table_bottom_row1 = ["Employer Registratrion No","","A/56108"]
        table_bottom_row2 = ["Half Year Period","","Jan to Dec 2023",""]
        table_bottom_row3 = ["No of Members","",no_of_employees,""]
        table_bottom_row4 = ["""Total Contribution 
        of Six Months""","",all_total_contribution_formated]
        table_bottom_row5 = ["No of Pages","",no_of_pages]
        table_bottom_row6 = ["Name of the Company","","""Ceylon Marine Services Holding Pvt Ltd"""]
        table_bottom_row7 = ["Address of the Company","","""No.72, St. Andrews Road, Modera, Colombo 15"""]
        table_bottom_row8 = ["Telephone No","","""0772594469"""]

        table_bottom_empty_row_1 = [""]

        table_bottom_row9 = ["I certify that all the particulars given above are true and correct"]
        table_bottom_empty_row_2 = [""]
        table_bottom_empty_row_3 = [""]
        table_bottom_row10 = ["...................................................................."]
        table_bottom_row11 = ["Signature of Employer and Official Seal"]
        table_bottom_row12 = ["Date __/__/___"]


        # table_data.append(table_row)
        table_data2.append(table_total_row)

        table_data2.append(table_bottom_row1)
        table_data2.append(table_bottom_row2)
        table_data2.append(table_bottom_row3)
        table_data2.append(table_bottom_row4)
        table_data2.append(table_bottom_row5)
        table_data2.append(table_bottom_row6)
        table_data2.append(table_bottom_row7)
        table_data2.append(table_bottom_row8)
        table_data2.append(table_bottom_empty_row_1)
        table_data2.append(table_bottom_row9)
        table_data2.append(table_bottom_empty_row_2)
        table_data2.append(table_bottom_empty_row_3)
        table_data2.append(table_bottom_row10)
        table_data2.append(table_bottom_row11)
        table_data2.append(table_bottom_row12)
        elements2 = []
        row_heights = [1*inch for i in range(4)]
        attendance_table = Table(table_data2,colWidths=[0.7*inch,1.2*inch,0.8*inch,0.9*inch,2.0*inch,0.8*inch,1.2*inch])
        attendance_table_styles = TableStyle(
            [
                ('GRID', (0, 4), (-1, 11), 1, colors.black), #Details Table
                ('GRID', (0, 13), (5, 20), 1, colors.black), #Summary Table
                ('FONT', (0, 0), (-1, 2), 'Helvetica-Bold',11),
                ('ALIGN', (0, 0), (-1, 2),'CENTER'), # Headings Center
                ('ALIGN', (0, 22), (-1, 22),'CENTER'), # I certify
                ('ALIGN', (0, 25), (-1, 25),'CENTER'), # ...........
                ('ALIGN', (0, 26), (-1, 26),'CENTER'), # Sign
                ('ALIGN', (0, 27), (-1, 27),'CENTER'), # Date

                ('SPAN', (0, 0), (-1, 0)),
                ('SPAN', (0, 1), (-1, 1)),
                ('SPAN', (0, 2), (-1, 2)),
                ('SPAN', (0, 3), (-1, 3)),


                ('SPAN', (0, 13), (1, 13)),
                ('SPAN', (0, 14), (1, 14)),
                ('SPAN', (0, 15), (1, 15)),
                ('SPAN', (0, 16), (1, 16)),
                ('SPAN', (0, 17), (1, 17)),
                ('SPAN', (0, 18), (1, 18)),
                ('SPAN', (0, 19), (1, 19)),
                ('SPAN', (0, 20), (1, 20)),


                ('SPAN', (2, 13), (5, 13)),
                ('SPAN', (2, 14), (5, 14)),
                ('SPAN', (2, 15), (5, 15)),
                ('SPAN', (2, 16), (5, 16)),
                ('SPAN', (2, 17), (5, 17)),
                ('SPAN', (2, 18), (5, 18)),
                ('SPAN', (2, 19), (5, 19)),
                ('SPAN', (2, 20), (5, 20)),

                ('SPAN', (0, 22), (-1, 22)),
                ('SPAN', (0, 25), (-1, 25)),
                ('SPAN', (0, 26), (-1, 26)),
                ('SPAN', (0, 27), (-1, 27)),

                ]
            
        )
        attendance_table.setStyle(attendance_table_styles)
        attendance_table.setStyle(TableStyle([('STYLE', (0,0), (-1,-1), 'my_cell_style')]))
        elements2.append(attendance_table)
        pdf2.build(elements2)
        buffer2.seek(0)



        merged_buffer = io.BytesIO()
        pdf_writer = PdfWriter()
        pdf1_reader = PdfReader(buffer)
        pdf2_reader = PdfReader(buffer2)

        for page_num in range(len(pdf1_reader.pages)):
            page = pdf1_reader.pages[page_num]
            pdf_writer.add_page(page)

        for page_num in range(len(pdf2_reader.pages)):
            page = pdf2_reader.pages[page_num]
            pdf_writer.add_page(page)

        pdf_writer.write(merged_buffer)
        merged_buffer.seek(0)


        return FileResponse(merged_buffer, as_attachment=True, filename=f"etf_report.pdf")
    
class EmployeeReport(LoginRequiredMixin,View):
    def get(self,request):
        return render(request,"employee_report.html")
    def post(self,request):
        emp_type =  request.POST["emp_type"]
        employees_list = Employee.objects.values("emp_id","name","appoinment_date","termination_date").filter(emp_type=emp_type)
        for employee in employees_list:
            joined_date = employee["appoinment_date"]
            resigned_date = employee["termination_date"]
            if joined_date and resigned_date:
                time_difference = (resigned_date.year - joined_date.year) * 12 + resigned_date.month - joined_date.month
                if time_difference > 12:
                    years = time_difference // 12
                    months = time_difference % 12
                    worked_time = (f"{years} years and {months} months") if years > 1 else (f"{years} year and {months} months")
                elif time_difference == 12:
                    worked_time = f"1 year"
                else:
                    worked_time = f"{time_difference} months"
            else:
                worked_time = ""
            employee["worked_time"] = worked_time


        file_name = f"Employee Report.pdf"
        title = f"Employee Report"
        buffer = io.BytesIO() 
        pdf = SimpleDocTemplate(buffer,pagesize = A4, title=title,showBoundary=1,leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0,)
        
        table_data = []
        document_heading = [f"Employee Report"]
        empty_row_heading =[""]
        table_data.append(document_heading)
        table_data.append(empty_row_heading)
        table_heading = ["""Employee ID""", 'Name','Joined Date',"""Resigned Date""","Worked Time"]
        
        table_data.append(table_heading)
        for emp in employees_list:
            table_row = [emp["emp_id"], emp["name"], emp["appoinment_date"],emp["termination_date"],emp["worked_time"]]
            table_data.append(table_row)
        elements = []
        
        attendance_table = Table(table_data,colWidths=[1.0*inch,2.5*inch,1.3*inch,1.3*inch,1.5*inch],rowHeights=[0.3*inch for i in range(len(employees_list)+3)])
        attendance_table_styles = TableStyle(
    [
        ('GRID', (0, 2), (-1, -1), 1, colors.black),
        ('FONT', (0, 0), (0, 0), 'Helvetica-Bold',15),
        ('FONT', (0, 2), (-1, -1), 'Helvetica',9),
        ('SPAN', (0, 0), (0, 0)),
        ('SPAN', (0, 0), (-1, 0)),

        ('ALIGN', (0, 0), (0,0),'CENTER'),
        ('ALIGN', (0, 2), (-1,2),'CENTER'),
        ('VALIGN', (0, 0), (-1, -1),'MIDDLE'),
        ]
    
)
        attendance_table.setStyle(attendance_table_styles)
        elements.append(attendance_table)
        pdf.build(elements)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=file_name)