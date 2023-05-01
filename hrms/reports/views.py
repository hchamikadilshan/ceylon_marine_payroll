from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse,FileResponse
from payroll.views import get_process_salary,calculate_salary,get_final_salary_details
from employee.models import Employee,Bank,BankBranch
from adminapp.models import Company
import locale
import io
from reportlab.lib.pagesizes import A4,landscape
from reportlab.platypus import SimpleDocTemplate,Table,TableStyle,Frame
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch,cm
import decimal

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
                elif employee_response[-1] == 0:
                    pass
                else:
                    epf_no = employee_response[-3]
                    name = employee_response[-5]
                    department = employee_response[-4]
                    basic_salary = employee_response[3]
                    br_allowance = employee_response[2]
                    epf_12 = (basic_salary + br_allowance) * 0.12
                    epf_8 =employee_response[5]
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
        
        employees_data = get_process_salary("multiple",year_month_split[1])
        for employee in employees_data:
            try :
                response = calculate_salary(employee[0],employee[1],employee[2],year_month_split[1])
                net_salary = "{:>9,.2f}".format(response[12])
                if response == "employee_finance_details_error":
                    payslips_record.append({"status":2})
                elif response == "Department Empty":
                    payslips_record.append({"status":3})
                elif response[-1] == 0:
                    pass
                elif (employee[0].bank == None or employee[0].branch == None or employee[0].bank_acc_no == "" or employee[0].bank_acc_name == "" ):
                    payslips_record.append({'emp_id':employee[0].emp_id,"name":employee[0].name,"month":year_month,'net_salary':net_salary,"status":4})
                else:
                    
                    payslips_record.append({'emp_id':employee[0].emp_id,"name":employee[0].name,"month":year_month,'net_salary':net_salary,"status":0})
            except (ValueError,IndexError):
                payslips_record.append({'emp_id':employee[0].emp_id,"name":employee[0].name,"month":year_month,"status":1})
        return JsonResponse({"data":payslips_record})
    
class BankTranferReportPDF(LoginRequiredMixin,View):
    login_url = '/accounts/login'
    def post(self,request):
        year_month = request.POST["month_year"]
        year_month_split = year_month.split('-')
        employees_data = get_process_salary("multiple",year_month_split[1])
        employee_records = []
        for employee in employees_data:
            try :
                
                response = calculate_salary(employee[0],employee[1],employee[2],year_month_split[1])
                net_salary = "{:>9,.2f}".format(response[12])
                if response == "employee_finance_details_error":
                    pass
                elif response == "Department Empty":
                    pass
                elif response[-1] == 0:
                    pass
                elif (employee[0].bank == None or employee[0].branch == None or employee[0].bank_acc_no == "" or employee[0].bank_acc_name == "" ):
                    pass
                else:    

                    employee_records.append([employee[0].emp_id,employee[0].name,employee[0].bank_acc_no,employee[0].bank.bank_name,employee[0].branch.branch_name,net_salary])
            except (ValueError,IndexError):
                pass
        file_name = "Bank_Transfer_Request.pdf"
        buffer = io.BytesIO() 
        pdf = SimpleDocTemplate(buffer,pagesize = landscape(A4), title="SPECIMEN Bank Transfer List",showBoundary=1,leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0,)
        table_data = []

        document_heading = [f"SPECIMEN Bank Transfer List"]
        empty_row_heading =[""]
        table_data.append(document_heading)
        table_data.append(empty_row_heading)
        table_heading = ["""No""", """EMPLOYEE
ID""","""EMPLOYEE 
NAME""","""ACCOUNT 
NO""","""BANK""",'BRANCH',"""NET 
SALARY"""]
        no = 1
        table_data.append(table_heading)
        for  employee_record in employee_records:
                table_data_row = ([no,  employee_record[0], employee_record[1], employee_record[2], employee_record[3], employee_record[4], employee_record[5]])
                table_data.append(table_data_row)
                no = no + 1
        


        elements = []
        attendance_table = Table(table_data,colWidths=[0.4*inch,1*inch,2.3*inch,1.5*inch,3*inch,1.3*inch,1.1*inch])
        attendance_table_styles = TableStyle(
            [
                ('GRID', (0, 2), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 2), (-1, 2),'CENTER'),
                ('VALIGN', (0, 2), (-1, 2),'MIDDLE'),
                ('FONT', (0, 2), (-1, 2), 'Helvetica-Bold',12),
                ('ALIGN', (-1, 3), (-1, -1),'RIGHT'),
                ]
            
        )
        attendance_table.setStyle(attendance_table_styles)
        elements.append(attendance_table)
        pdf.build(elements)
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
        # pdf = canvas.Canvas(buffer)
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



        


        # Employee Data Table Frame
        employees_data = get_process_salary("multiple",month)
        data_list = []
        i=1
        total_contribution = 0
        for employee in employees_data:
            try:
                if employee[2]["epf_type"] == "1": # type: ignore
                    
                    try :
                        response = calculate_salary(employee[0],employee[1],employee[2],year_month_split[1])
                        net_salary = "{:>9,.2f}".format(response[12])
                        if response == "employee_finance_details_error":
                            pass
                        elif response == "Department Empty":
                            pass
                        elif response[-1] == 0:
                            pass
                        else:
                            fixed_basic_salary = response[2] + response[3]
                            total_earning = "{:>9,.2f}".format(fixed_basic_salary)

                            employees = fixed_basic_salary * 0.08
                            employees_string = "{:>9.2f}".format(fixed_basic_salary * 0.08)
                            employees_int = int(fixed_basic_salary * 0.08)
                            employees_float = employees_string[-2:]

                            employers = fixed_basic_salary * 0.12
                            employers_string = "{:>9.2f}".format(employers)
                            employers_int = int(employers)
                            employers_float = employers_string[-2:]

                            total_epf =  employers + employees
                            total_epf_string = "{:>9.2f}".format(total_epf)
                            total_epf_int = int(total_epf)
                            total_rpf_float = total_epf_string[-2:]
                            # if response[11] > fixed_basic_salary:
                            #     total_earning = "{:>9,.2f}".format(fixed_basic_salary)

                            #     employees = fixed_basic_salary * 0.08
                            #     employees_string = "{:>9.2f}".format(fixed_basic_salary * 0.08)
                            #     employees_int = int(fixed_basic_salary * 0.08)
                            #     employees_float = employees_string[-2:]

                            #     employers = fixed_basic_salary * 0.12
                            #     employers_string = "{:>9.2f}".format(employers)
                            #     employers_int = int(employers)
                            #     employers_float = employers_string[-2:]

                            #     total_epf =  employers + employees
                            #     total_epf_string = "{:>9.2f}".format(total_epf)
                            #     total_epf_int = int(total_epf)
                            #     total_rpf_float = total_epf_string[-2:]
                                
                            # else:
                            #     total_earning = "{:>9,.2f}".format(response[11])

                            #     employees = response[11] * 0.08
                            #     employees_string = "{:>9.2f}".format(employees)
                            #     employees_int = int(response[11] * 0.08)
                            #     employees_float = employees_string[-2:]
                                
                            #     employers = response[11] * 0.12
                            #     employers_string = "{:>9.2f}".format(employers)
                            #     employers_int = int(employers)
                            #     employers_float = employers_string[-2:]

                            #     total_epf =  employers + employees
                            #     total_epf_string = "{:>9.2f}".format(total_epf)
                            #     total_epf_int = int(total_epf)
                            #     total_rpf_float = total_epf_string[-2:]
                            total_contribution += total_epf    
                            name = response[-5]
                            epf_no = response[-3]
                            nic_no = response[-7]
                            data_list.append([name,nic_no,epf_no,total_epf_int,total_rpf_float,employers_int,employers_float,employees_int,employees_float,total_earning])
                            i +=1
                    except (ValueError,IndexError):
                        pass
            except TypeError:
                pass
        # Right Frame 
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
        table = Table(table_data,colWidths=[2.7*inch,1.1*inch,0.7*inch,0.4*inch,0.3*inch,0.4*inch,0.3*inch,0.4*inch,0.3*inch,0.8*inch])
        table_styles = TableStyle(
            [
                ('FONT', (0, 0), (-1, -1), 'Helvetica',9.1),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold',10),
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
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f"{year_month}-epf-C-Form.pdf")
 
        
      