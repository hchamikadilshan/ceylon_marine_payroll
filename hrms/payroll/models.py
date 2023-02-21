from django.db import models
from employee.models import Employee
# Create your models here.


class SalaryAdvance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    amount= models.FloatField()

class Alllowance(models.Model):
    Employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.FloatField()
    remark = models.CharField(max_length=200, blank=True)

