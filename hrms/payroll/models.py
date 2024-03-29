from django.db import models
from employee.models import Employee
from datetime import datetime
# Create your models here.


class SalaryAdvance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.now())
    amount= models.FloatField()
    time_stamp = models.DateTimeField()
    status = models.BooleanField(default=True)

class Alllowance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.now())
    amount = models.FloatField()
    description = models.CharField(max_length=200, blank=True)
    time_stamp = models.DateTimeField()
    status = models.BooleanField(default=True)

class Deduction(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.now())
    amount = models.FloatField()
    description = models.CharField(max_length=200, blank=True)
    time_stamp = models.DateTimeField()
    status = models.BooleanField(default=True)

