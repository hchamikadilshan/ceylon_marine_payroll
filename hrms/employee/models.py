from django.db import models


# Create your models here.
class Employee(models.Model):
    emp_id = models.CharField(max_length=10,primary_key=True)
    emp_type = models.CharField(max_length=60)
    emp_title = models.CharField(default="", max_length=50),
    name = models.CharField(max_length=100)
    epf_no = models.CharField(max_length=10)
    nic_no = models.CharField(max_length=15)
    appoinment_date = models.DateField()
    termination_date = models.DateField()
    address = models.CharField(max_length=50)
    mobile_no = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    bank_name = models.CharField(max_length=50)
    bank_branch = models.CharField(max_length=20)
    bank_acc_name = models.CharField(max_length=20)
    bank_acc_no = models.CharField(max_length=15)
    active_status = models.BooleanField(default=True)

class EmployeeFinance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    daily_payment = models.FloatField()
    ot_payment_rate = models.FloatField()
    fixed_allowance = models.FloatField()
    leave_payment = models.FloatField()
    br_payment = models.FloatField()
    epf = models.FloatField()
    # advance_limit = models.FloatField()
    room_charge =models.FloatField()
    staff_welf_contribution = models.FloatField()
    submit_date = models.DateTimeField()
    
