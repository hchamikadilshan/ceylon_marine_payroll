from django.db import models
from adminapp.models import Department
import datetime

# Create your models here.
class Bank(models.Model):
    bank_id = models.CharField(primary_key=True,max_length=4)
    bank_name = models.CharField(max_length=150)

    def __str__(self):
        return self.bank_name

class BankBranch(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE,null=True)
    branch_id = models.CharField(max_length=4)
    branch_name = models.CharField(max_length=100)

class Employee(models.Model):
    emp_id = models.CharField(max_length=10,primary_key=True)
    emp_title = models.CharField(default="", max_length=50),
    emp_type = models.IntegerField(default=0)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100,default="")
    dprtmnt = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    epf_no = models.CharField(max_length=10, default="")
    nic_no = models.CharField(max_length=15, default="")
    appoinment_date = models.DateField(null=True)
    termination_date = models.DateField(null=True)
    address = models.CharField(max_length=50,default="")
    mobile_no = models.CharField(max_length=15, default="")
    email = models.EmailField(max_length=50, default="")
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, null=True)
    branch = models.ForeignKey(BankBranch, on_delete=models.CASCADE, null=True)
    bank_name = models.CharField(max_length=50, default="")
    bank_branch = models.CharField(max_length=20, default="")
    bank_acc_name = models.CharField(max_length=20, default="")
    bank_acc_no = models.CharField(max_length=15,default="")
    active_status = models.IntegerField(default=1)


class EmployeeFinance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    daily_payment = models.FloatField(default=0)
    ot_payment_rate = models.FloatField(default=0)
    epf_type = models.CharField(max_length=2,default="1")
    # fixed_allowance = models.FloatField()
    basic_salary = models.FloatField(default=0)
    br_payment = models.FloatField()
    epf = models.FloatField()
    # advance_limit = models.FloatField()
    room_charge =models.FloatField()
    staff_welf_contribution = models.FloatField()
    submit_date = models.DateTimeField()
    effective_from = models.DateField(default=datetime.date(2023, 1, 1))
    reason = models.CharField(max_length=100,default="")
    morning_ot = models.CharField(max_length=2,default="0")
    production_allowance =  models.FloatField(default=0)







    
